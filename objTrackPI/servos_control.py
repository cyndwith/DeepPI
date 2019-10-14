from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

import RPi.GPIO as GPIO
import busio
import time

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

class ServosControl():
    def __init__(self):
        # Initialize I2C
        self.pwm_freq = 50    # setting it to 50Hz 50% dudty cycle will be 1.5mv
        self.min_pulse = 900  # 900ms 
        self.max_pulse = 2000 # 2000ms 
        self.actuation_range  = 90
        self.direction_center = 45
        self.direction_stop = 0
        self.sleep = 0.5
    
    def setup(self, ch):
        self.servo = servo.Servo(pca.channels[ch], min_pulse=900, max_pulse=2000, actuation_range=90)
        return servo

    def disable(self):
        GPIO.cleanup()
    
    # steer_index : -20 to 20, it gets clamped
    def set_servo_angle(self, angle):
        print("servo_angle:", angle)
        self.servo.angle = angle
        time.sleep(self.sleep)

