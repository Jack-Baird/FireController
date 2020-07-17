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

#TODO: Implement burst-fire mode

import machine
from time import sleep

# set up pins
L3 = machine.Pin(5, machine.Pin.IN) # D1
R3 = machine.Pin(4, machine.Pin.IN) # D2
RTin = machine.Pin(14, machine.Pin.IN) # D5
RTout = machine.Pin(12, machine.Pin.OUT) # D6
LED = machine.Pin(13, machine.Pin.OUT) # D7

RTout.value(0)
LED.value(1)

mod_active = 0 # bool mod state
l3_active = 0 # bool L3 state
r3_active = 0 # bool R3 state
DELAY = 0.05 # delay between shots when active
DEBOUNCE = 0.2

def led_flash(style):
    """
    Controls the main LED to signal activation/deac of mod
    """
    if style:
        for i in range(2):
            LED.value(0)
            sleep(0.5)
            LED.value(1)
            sleep(0.5)

    if not style:
        LED.value(0)
        sleep(1)
        LED.value(1)

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

def trigger_normal(p):
    """
    Normal mode trigger control
    """
    while True:
        fire = RTin.value()
        RTout.value(fire)
        if not fire:
            break

def toggle_mod_state():
    """
    Toggles in and out of rapid-fire mode
    """
    global mod_active
    mod_active = 1 if mod_active == 0 else 0
    if mod_active:
        print('Mod ACTIVE')
        led_flash(1)
    else:
        print('Mod INACTIVE')
        led_flash(0)

def sample_sticks():
    """
    Polls L3 and R3 for mode-change command
    """
    state = L3.value() + R3.value() # sample L3 and R3
    return 1 if state == 2 else 0 # bool 1 if both sticks pressed

# main loop
while True:
    # polling for mode-change command
    switch1 = sample_sticks()
    if switch1:
        toggle_mod_state()
        switch1 = 0
        sleep(DEBOUNCE)

    if mod_active:
        # steps into rapid-fire mode
        while True:
            RTin.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_auto)

            # polling for mode-change command
            switch2 = sample_sticks()
            if switch2:
                # steps out of rapid-fire mode
                toggle_mod_state()
                switch2 = 0
                sleep(DEBOUNCE)
                break

    RTin.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_normal) # listens for normal trigger use
