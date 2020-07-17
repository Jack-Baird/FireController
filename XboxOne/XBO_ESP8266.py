"""
______ _            _____             _             _ _
|  ___(_)          /  __ \           | |           | | |
| |_   _ _ __ ___  | /  \/ ___  _ __ | |_ _ __ ___ | | | ___ _ __
|  _| | | '__/ _ \ | |    / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| |   | | | |  __/ | \__/\ (_) | | | | |_| | | (_) | | |  __/ |
\_|   |_|_|  \___|  \____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|
                                               Created by MNNRD

A MircoPython script for use with ESP8266 boards to provide custom
fire modes for new-style Xbox One controllers.
"""

# -------------------------------------------------
# Edit these constants for customisation!
# -------------------------------------------------
DELAY = 0.05 # delay (secs) between shots when active
BURST = 3 # number of rounds in burst-fire mode
DEBOUNCE = 0.2 # switch debounce time
ENABLE_LED = False # use to enable / disable LED
# -------------------------------------------------
# -------------------------------------------------

import machine
from time import sleep

# set up pins
L3 = machine.Pin(5, machine.Pin.IN) # D1
R3 = machine.Pin(4, machine.Pin.IN) # D2
RTin = machine.Pin(14, machine.Pin.IN) # D5
RTout = machine.Pin(12, machine.Pin.OUT) # D6
LED = machine.Pin(13, machine.Pin.OUT) if ENABLE_LED else None # D7

RTout.value(0)
try:
    LED.value(1)
    print('LED control enabled')
except Exception as e:
    print('LED control disabled')


fc_mode = 0 # (0) Off, (1) Burst, (2) Auto
l3_active = 0 # bool L3 state
r3_active = 0 # bool R3 state

def led_flash(style):
    """
    Controls the main LED to signal ac/deac of mod
    """
    if style == 0:
        LED.value(0)
        sleep(1.5)
        LED.value(1)

    if style == 1:
        LED.value(0)
        sleep(0.5)
        LED.value(1)

    if style == 2:
        for i in range(2):
            LED.value(0)
            sleep(0.5)
            LED.value(1)
            sleep(0.5) if i < 1 else None

def trigger_on(p):
    """
    Rapid-fire mode trigger pressed
    """
    RTout.value(1)

def trigger_off(p):
    """
    Rapid-fire mode trigger released
    """
    RTout.value(0)

def trigger_auto(p):
    """
    Rapid-fire mode trigger control
    """
    while True:
        trigger_on(p)
        trigger_off(p)
        if RTin.value() == 0:
            break
        else:
            sleep(DELAY)

def trigger_burst(p):
    """
    Burst-fire mode trigger control
    """
    for i in range(BURST):
        trigger_on(p)
        trigger_off(p)

def trigger_normal(p):
    """
    Normal mode trigger control
    """
    while True:
        fire = RTin.value()
        RTout.value(fire)
        if not fire:
            break

def cycle_fc_mode():
    """
    Cycles fire modes
    """
    global fc_mode
    if fc_mode == 0:
        fc_mode = 1
        print('Burst-fire Active')
        led_flash(1) if ENABLE_LED else None

    elif fc_mode == 1:
        fc_mode = 2
        print('Rapid-fire Active')
        led_flash(2) if ENABLE_LED else None

    elif fc_mode == 2:
        fc_mode = 0
        print('Fire Controller Inactive')
        led_flash(0) if ENABLE_LED else None        

def sample_sticks():
    """
    Polls L3 and R3 for mode-change command
    """
    state = L3.value() + R3.value() # sample L3 and R3
    return 1 if state == 2 else 0 # bool 1 if both sticks pressed

# main loop
while True:
    # polling for mode-change command
    toggle = sample_sticks()
    if toggle:
        cycle_fc_mode()
        toggle = 0
        sleep(DEBOUNCE) #? Necessary?

    if fc_mode == 1:
        # steps into burst-fire mode
        while True:
            # listens for trigger in burst-fire mode
            RTin.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_burst)

            # polling for mode-change command
            toggle = sample_sticks()
            if toggle:
                # toggles fire-mode selector
                cycle_fc_mode()
                toggle = 0
                sleep(DEBOUNCE)

            if fc_mode == 2:
                # steps into rapid-fire mode
                while True:
                    # listens for trigger in rapid-fire mode
                    RTin.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_auto)

                    # polling for mode-change command
                    toggle = sample_sticks()
                    if toggle:
                        # toggles fire-mode selector
                        cycle_fc_mode()
                        toggle = 0
                        sleep(DEBOUNCE)
                        break
        
                break

    # listens for normal trigger use
    RTin.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_normal)
