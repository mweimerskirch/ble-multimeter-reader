import bluepy.btle as btle
import sys


class BTDelegate(btle.DefaultDelegate):
    buffer = b""

    value = ""
    unit = ""

    label_rel = ""
    label_ac_dc = ""
    label_max_min_avg = ""
    label_hold = ""

    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, c_handle, data):
        self.buffer = self.buffer + data
        if len(self.buffer) >= 15:
            self.analyseDataFromMeter(self.buffer)
            self.buffer = b""

    def analyseDataFromMeter(self, buffer):
        # Read the unit
        self.unit = self.parse_unit(buffer)

        # Read the status of the "HOLD" button
        if buffer[12] & 64 != 0:
            self.label_hold = "HOLD"
        else:
            self.label_hold = ""

        # Read other labels, like MIN/MAX/AUTO, etc
        self.parse_labels(buffer[13])

        # Read the value (in reversed order)
        value = ""
        for i in [8, 7, 6, 5]:
            temp_value = buffer[i] & 255
            if temp_value is not None:
                value += str(temp_value)

        # Handle special value representing "OL"
        if value == "1101011":
            value = "OL"
        else:
            # Read the location of the decimal point and handle a few special cases
            point_temp = buffer[9] & 255

            if point_temp >= 4 or point_temp <= 0:
                if len(value) == 2:
                    point_temp = 1
                else:
                    point_temp = 3

            point = len(value) - point_temp

            if len(value) > point > 0:
                value = value[:point] + "." + value[point:]

        # Check if the value is negative
        if buffer[12] & 128 != 0:
            value = '-' + value

        self.value = value

        self.printData()

    def printData(self):
        print(self.value, self.unit, self.label_ac_dc, self.label_max_min_avg, self.label_hold)

    def parse_unit(self, buffer):
        main_unit = self.get_main_unit(buffer[10] & 255)
        secondary_unit = self.get_secondary_unit(buffer[11] & 255)
        return secondary_unit + main_unit

    @staticmethod
    def get_main_unit(number):
        main_units = {
            1: "V",
            2: "A",
            3: "Ω",
            4: "Hz",
            5: "F",
            6: "Ω",
            7: "V",
            8: "°C",
            9: "°F",
            10: "%",
        }
        return main_units[number]

    @staticmethod
    def get_secondary_unit(number):
        secondary_units = {
            0: "",
            1: "K",
            2: "M",
            3: "n",
            4: "u",
            5: "m",
            6: "m",
        }
        return secondary_units[number]

    def parse_labels(self, value):
        value_ac_dc = (value & 192) >> 6  # 192 = 0b11000000
        value_rel = (value & 63) >> 4  # 63  = 0b00111111
        value_max_min_avg = (value & 15) >> 2  # 15  = 0b00001111
        value_peak = value & 3  # 3   = 0b00000011

        if value_ac_dc == 1:
            self.label_ac_dc = "DC"
        elif value_ac_dc == 2:
            self.label_ac_dc = "AC"
        elif value_ac_dc == 3:
            self.label_ac_dc = "AC+DC"

        if value_rel == 1:
            self.label_max_min_avg = "AUTO"
        elif value_rel == 2:
            self.label_max_min_avg = "REL"

        if value_max_min_avg == 1:
            self.label_max_min_avg = "MAX"
        elif value_max_min_avg == 2:
            self.label_max_min_avg = "MIN"
        elif value_max_min_avg == 3:
            self.label_max_min_avg = "AVG"

        if value_peak == 1:
            self.label_max_min_avg = "PEAK MAX"
        elif value_peak == 2:
            self.label_max_min_avg = "PEAK MIN"
        elif value_peak == 3:
            self.label_max_min_avg = ""


if __name__ == '__main__':
    bleDevice = None

    if len(sys.argv) >= 2:
        bleDevice = sys.argv[1]
    else:
        print('Usage: main.py 00:00:00:00:00:00')
        sys.exit(2)

    print("Connecting to device", bleDevice)

    p = btle.Peripheral(bleDevice)

    bt_delegate = BTDelegate()

    p.setDelegate(bt_delegate)
    p.writeCharacteristic(0x0015, b"\x01\x00", True)

    # Wait for new data in a loop.
    while True:
        if p.waitForNotifications(1.0):
            continue

        # Waiting for new values (while "HOLD" is pushed): just repeat the last value.
        bt_delegate.printData()
