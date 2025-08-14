# this is a simple Gpio import and export script for a project of mine feel free to use it and customize it
# main use cases:
# Export a pin
# Set Pin to High or Low
# unexport a pin 

import os

# Physical pin numbers 1–40, index 0 unused for convenience
OPiZero2WLayout = [
    " ",    # 1   3.3V
    " ",    # 2   5V
    264,    # 3   SDA.1
    " ",    # 4   5V
    263,    # 5   SCL.1
    " ",    # 6   GND
    269,    # 7   PWM3
    224,    # 8   TXD.0
    " ",    # 9   GND
    225,    # 10  RXD.0
    226,    # 11  TXD.5
    257,    # 12  PI01
    227,    # 13  RXD.5
    " ",    # 14  GND
    261,    # 15  TXD.2
    270,    # 16  PWM4
    " ",    # 17  3.3V
    228,    # 18  PH04
    231,    # 19  MOSI.1
    " ",    # 20  GND
    232,    # 21  MISO.1
    262,    # 22  RXD.2
    230,    # 23  SCLK.1
    229,    # 24  CE.0
    " ",    # 25  GND
    233,    # 26  CE.1
    266,    # 27  SDA.2
    265,    # 28  SCL.2
    256,    # 29  PI00
    " ",    # 30  GND
    271,    # 31  PI15
    267,    # 32  PWM1
    268,    # 33  PI12
    " ",    # 34  GND
    258,    # 35  PI02
    76,     # 36  PC12
    272,    # 37  PI16
    260,    # 38  PI04
    " ",    # 39  GND
    259     # 40  PI03
]


CustomLayout = OPiZero2WLayout[:]  # Same for now

UsingPins = "OPiZero2W"


def _resolve_pin(pin_num):
    """Convert board pin to GPIO number based on layout."""
    layouts = {
        "OPiZero2W": OPiZero2WLayout,
        "Custom": CustomLayout
    }
    layout = layouts.get(UsingPins)
    if UsingPins == "GPIO":
        return pin_num
    if not layout:
        raise ValueError(f"Unsupported layout: {UsingPins}")
    gpio = layout[pin_num - 1]
    if gpio == " ":
        raise ValueError(f"Pin {pin_num} is not usable (GND/VCC)")
    return gpio


def pinmode(pin_num, mode):
    assert mode in ["in", "out"], "Mode must be 'in' or 'out'"
    gpio = _resolve_pin(pin_num)
    try:
        with open("/sys/class/gpio/export", "w") as f:
            f.write(str(gpio))
    except FileExistsError:
        pass
    with open(f"/sys/class/gpio/gpio{gpio}/direction", "w") as f:
        f.write(mode)


def write(pin_num, value):
    assert value in [0, 1], "Value must be 0 or 1"
    gpio = _resolve_pin(pin_num)
    with open(f"/sys/class/gpio/gpio{gpio}/value", "w") as f:
        f.write(str(value))


def readpin(pin_num):
    gpio = _resolve_pin(pin_num)
    try:
        with open(f"/sys/class/gpio/gpio{gpio}/value", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None


def unexport(pin_num):
    gpio = _resolve_pin(pin_num)
    with open("/sys/class/gpio/unexport", "w") as f:
        f.write(str(gpio))


def boardmode(mode):
    global UsingPins
    assert mode in ["OPiZero2W", "Custom", "GPIO"]
    UsingPins = mode
