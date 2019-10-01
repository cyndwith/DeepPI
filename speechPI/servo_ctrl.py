import RPi.GPIO as GPIO
import time

servoPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
delay_time=0.2
p = GPIO.PWM(servoPIN, 333) # GPIO 17 for PWM with 50Hz
p.start(34)
time.sleep(delay_time)
p.ChangeDutyCycle(0)# Initialization
time.sleep(3)
try:
    print("here---------------->>>>>")
    p.ChangeDutyCycle(34)
    time.sleep(delay_time)
    p.ChangeDutyCycle(0)
    
    time.sleep(4)
    
    p.ChangeDutyCycle(65)
    time.sleep(delay_time)
    p.ChangeDutyCycle(0)
    
   
    #time.sleep(0.5)

except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
