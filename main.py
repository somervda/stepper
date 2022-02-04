# Main routine for experimenting and testing my stepper motor interface

import time
import sys
from rotary_irq import RotaryIRQ
from machine import Pin, PWM
ena = Pin(20, Pin.OUT)  # blue
dir = Pin(19, Pin.OUT)  # Yellow
pwm = PWM(Pin(18))  # green
# Break out of main loop when this pin is grounded
isBreakPin = Pin(0, Pin.IN, Pin.PULL_UP)
# Reset motor to speed = 0 when this pin is grounded
isResetPin = Pin(14, Pin.IN, Pin.PULL_UP)
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
val_old = r.value()
print("Starting...")
while True:
    val_new = r.value()
    if isBreakPin.value() == 0:
        break
    if isResetPin.value() == 0:
        r.reset()
        val_new = 0

    if val_old != val_new:
        val_old = val_new
        print('result =', val_new)
        # Set the PWM frequency - I want to support max of 600RPM or 6RPS
        # The TB6600 is set to 1600 steps per revolution (Using microstepping)
        #  so max frequency needs to be 1600 * 6 = 9600Hz
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
    time.sleep_ms(50)
print("End")
