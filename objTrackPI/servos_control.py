import RPi.GPIO as GPIO
import time

class ServosControl():
    def __init__(self):
        self.direction_servo_pin=18  # pwm pin on raspberry pi (BCM mode)
        self.direction_servo_delay=0.2 # a delay of 200 ms to be able to take a full turn
        self.direction_lmax=35  # min of 33% duty_cycle
        self.direction_rmax=65  # max of 65% duty cycle
        self.direction_center=50
        self.direction_stop=0
        self.pwm_freq=333 #setting it to 333Hz 50% dudty cycle will be 1.5mv
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.direction_servo_pin, GPIO.OUT)
        GPIO.output(self.direction_servo_pin,0)
        self.pwm = GPIO.PWM(self.direction_servo_pin, self.pwm_freq )
        self.pwm.start(0)  #starting with 0 degrees / straight
        self.trim = 0

    def disable(self):
        GPIO.cleanup()

    def steer_to_angle(self, steer_index):
        if steer_index <= 0:
            steer_index = max(steer_index+self.direction_center,self.direction_lmax)
        else:
            steer_index = min(steer_index+self.direction_center,self.direction_rmax)
        self.steer_angle = self.trim+steer_index
        self.pwm.ChangeDutyCycle(self.steer_angle)
        time.sleep(self.direction_servo_delay)
        self.pwm.ChangeDutyCycle(self.direction_stop)


    def steer_right(self,angle):
        if angle>30 or angle<0 :
            print("Angle should range from 0-30 0 neing the center of the ")
        self.steer_to_angle(angle//2)
        return
    def steer_left(self,angle):
        if angle>30 or angle<0 :
            print("Angle should range from 0-30 0 neing the center of the ")
        self.steer_to_angle(-1* angle//2)
        return
