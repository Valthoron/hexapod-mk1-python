# Hexapod MK1 - "Findir"
This is a controller program for a hexapod (six-legged) robot. Mechanical design of the robot can be found here: https://github.com/SmallpTsai/hexapod-v2-7697. Electronics and software is custom.

## Features
- Control algorithm running in soft real-time under Raspbian Lite on Raspberry Pi Zero W
- Movement on three axes: Forward-back, sidewards, and left-right turn
- Adjustable movement speed
- Adjustable body height and attitude
- Adjustable leg lifting height
- I2C communication with two [Waveshare Servo Driver boards](https://www.waveshare.com/servo-driver-hat.htm) (PCA9685) to run a total of 18 servos
- I2C communication with an Arduino Nano to read command signals from a [Sanwa SD-10G](http://www.sanwa-denshi.com/rc/sky/propo/sd-10g.html) radio controller for remote control
- XML-based configuration file for servo calibration

## Dependencies
- Python 3.7.3
- [NumPy](https://numpy.org/) 1.16.2
- [mgen](https://pypi.org/project/mgen/) 1.2.0
- [picamera](https://pypi.org/project/picamera/) 1.13

## How To Run
Main controller routine is `python3 Main.py`.

To calibrate servos, `python3 ServoCalibration.py` commands all joints to preset angles and continually reads the configuration XML for bias values.
