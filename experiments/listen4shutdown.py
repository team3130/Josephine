#!/usr/bin/env python

"""
It's possible to advance this research and make it functional
But it's really already done at
https://github.com/Howchoo/pi-power-button
Very easy to install
"""

import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(3, GPIO.FALLING)

subprocess.call(['shutdown', '-h', 'now'], shell=False)
