import time
import tools
import ArduinoControls
import PCA9685

I2C_CHANNEL = 1
I2C_ADDRESS_ARDUINOCONTROLS = 0x04
I2C_ADDRESS_SERVODRIVER1 = 0x40

device_Controls = ArduinoControls.ArduinoControls(I2C_CHANNEL, I2C_ADDRESS_ARDUINOCONTROLS)
device_ServoDriver1 = PCA9685.PCA9685(I2C_ADDRESS_SERVODRIVER1, debug=False)

device_ServoDriver1.setPWMFreq(50)

pulseWidth = 1000

while 1:
    device_Controls.read_controls()

    # for axis in range(5):
    #     value = device_Controls.get_axis(axis)
    #     print("{0:5.2f}".format(value), end = " ")
    #
    # for switch in range(5):
    #     value = device_Controls.get_switch(switch)
    #     print(value, end = " ")
    #
    # print("")

    #pulseWidth = tools.ramp(round(device_Controls.get_axis(0), 1), -1, 1000, 1, 2000)
    if (device_Controls.get_axis(0) < -0.1):
        pulseWidth += 100 * (device_Controls.get_axis(0) + 0.1)
    elif (device_Controls.get_axis(0) > 0.1):
        pulseWidth += 100 * (device_Controls.get_axis(0) - 0.1)

    pulseWidth = tools.saturate(pulseWidth, 500, 2350)

    device_ServoDriver1.setServoPulse(0, pulseWidth)

    time.sleep(0.05)
