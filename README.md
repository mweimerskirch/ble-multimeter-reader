# BLE Multimeter reader

This is a tool to read out values from a PeakTech 3445 bluetooth multimeter.

I bought the meter a couple of weeks ago and was rather unhappy with the mobile app.
I would also have preferred a desktop or CLI application, so I just started writing my own.

## Disclaimer

This is work in process.
Consider it an early alpha.
Some values are not yet read correctly, so there are known bugs.
Don't just yet trust the values you get.

The tool might work with other meters, or completely brick them.

Use at your own risk.

## Installation

You can use pip to install the required dependencies.

```bash
pip3 install bluepy
```

## Usage

To use it, you can simply run the main.py file as follows.
Don't forget to replace "00:00:00:00:00:00" with the MAC address of your meter.

```shell script
python3 main.py --device="00:00:00:00:00:00"
```

## Contributing
Pull requests are welcome.
Before starting with a larger changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
