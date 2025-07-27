import RPi.GPIO as GPIO
import socket_setup
import logging
import time

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

socket_setup.setup()

logging.info("Sending code 1111 socket 1 on")
GPIO.output (13, True)
GPIO.output (16, True)
GPIO.output (15, True)
GPIO.output (11, True)

time.sleep(2)

logging.info("Sending code 0111 socket 1 off")
GPIO.output (13, False)
GPIO.output (16, True)
GPIO.output (15, True)
GPIO.output (11, True)
