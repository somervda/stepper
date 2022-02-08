# Main routine for experimenting and testing my stepper motor interface

import freesansnum35
import time
import sys
from rotary_irq import RotaryIRQ
from machine import Pin, PWM, I2C
from ssd1306 import SSD1306_I2C
from writer import Writer

STEPS_PER_REVOLUTION = 1600  # Set on stepper motor driver
STEPPER_GEARING = 14  # 14:1 gearing on stepper motor
LEAD_SCREW_TPI = 17  # 17 threads per inch
# Font file converted to a bitmap (for ascii 32-57) 35 pixel height works well for this display
# See https://github.com/peterhinch/micropython-font-to-py
OLED_WIDTH = 128
OLED_HEIGHT = 64

display_mode = 1  # 1=Revolutions Per Minute, 2=Revolutions Per Second, 3=Inches Per Mimute

# Set up the i2c0 object to represent the i2c bus 0
i2c0 = I2C(0, scl=Pin(17), sda=Pin(16))
# Set up the object representing the oled
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c0, addr=0x3C)
wri = Writer(oled, freesansnum35, verbose=False)
oled.fill(0)


ena = Pin(20, Pin.OUT)  # blue
dir = Pin(19, Pin.OUT)  # Yellow
pwm = PWM(Pin(18))  # green
# Break out of main loop when this pin is grounded
isBreakPin = Pin(0, Pin.IN, Pin.PULL_UP)
# Reset motor to speed = 0 when this pin is grounded
isResetPin = Pin(14, Pin.IN, Pin.PULL_UP)
# Change display Mode
displayModePin = Pin(9, Pin.IN, Pin.PULL_UP)
dir.value(0)
ena.value(1)  # Low signal activates ENA
pwm.freq(100)  # 100Hz
pwm.duty_u16(32768)  # duty 50% (65535/2)
# pwm.duty_u16(1000)


r = RotaryIRQ(pin_num_clk=13,
              pin_num_dt=12,
              min_val=-100,
              max_val=100,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_BOUNDED)

r.set(value=0)
val_old = -1000
old_displayModePin = displayModePin.value()
print("Starting...")
while True:
    val_new = r.value()
    if isBreakPin.value() == 0:
        break
    if isResetPin.value() == 0:
        r.reset()
        val_new = 0

    if val_old != val_new or old_displayModePin != displayModePin.value():
        if old_displayModePin != displayModePin.value():
            # display mode switch has been pressed or released
            # only update display mode on the press  (value = 0)
            if displayModePin.value() == 0:
                display_mode += 1
                if display_mode == 4:
                    display_mode = 1
            # Update the old_displayModePin value to be able to debounce the presses
            old_displayModePin = displayModePin.value()
        val_old = val_new
        print('result =', val_new)
        # Set the PWM frequency - I want to support max (Un-geared) of 360RPM or 6RPS
        # The TB6600 is set to STEPS_PER_REVOLUTION (1600) steps per revolution (Using microstepping)
        #  so max frequency needs to be STEPS_PER_REVOLUTION * 6 = 9600Hz
        # Max value from encoder is 100 so need to multiple by 96 to get the 9600Hz max speed
        pulseRatio = 96
        if(abs(val_new) > 0):
            pwm.freq(abs(val_new * pulseRatio))
            pwm.duty_u16(32768)
        if(val_new > 0):
            ena.value(0)
            dir.value(1)
        elif(val_new < 0):
            ena.value(0)
            dir.value(0)
        else:
            ena.value(1)
        if display_mode == 1:
            speed = (val_new * pulseRatio * 60) / \
                (STEPS_PER_REVOLUTION * STEPPER_GEARING)
            prompt = "Revs/Minute"
            significant_digits = 1
        elif display_mode == 2:
            speed = (val_new * pulseRatio) / \
                (STEPS_PER_REVOLUTION * STEPPER_GEARING)
            prompt = "Revs/Second"
            significant_digits = 2
        else:
            speed = (val_new * pulseRatio * 60) / \
                (STEPS_PER_REVOLUTION * STEPPER_GEARING * LEAD_SCREW_TPI)
            prompt = "Inches/Minute"
            significant_digits = 2
        oled.fill(0)
        oled.line(0, 15, oled.width - 1, 15, 1)
        Writer.set_textpos(oled, 0, 0)
        # Use string format (:^16) to center prompt in 16 character line
        oled.text("{:^16s}".format(prompt),  0, 0)
        Writer.set_textpos(oled, 25, 0)
        if significant_digits == 1:
            # Use string format (:>8) to right align speed in a 8 character space
            wri.printstring("{:>8s}".format('%.1f' % speed))
        else:
            wri.printstring("{:>8s}".format('%.2f' % speed))
        oled.show()
    time.sleep_ms(50)
print("End")
