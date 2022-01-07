# Main routine for experimenting and testing my stepper motor interface

import time
import sys
from rotary_irq import RotaryIRQ


r = RotaryIRQ(pin_num_clk=15,
              pin_num_dt=14,
              min_val=-100,
              max_val=100,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_BOUNDED)

r.set(value=0)
val_old = r.value()
print("Starting...")
while True:
    val_new = r.value()

    if val_old != val_new:
        val_old = val_new
        print('result =', val_new)

    time.sleep_ms(50)
print("End")
