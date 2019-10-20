# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO

class GarageDoor:
    def __init__(self):
        print("GarageDoor Initialization\n")
        self.classNames = { 0: 'closed', 1: 'open'}
        # load the model
        # self.model = cv2.dnn.readNetFromTensorflow('myGarage.pb', 'myGarage.pbtxt')
        self.model = cv2.dnn.readNetFromTensorflow('myGarage.pb')
        # object BBox
        self.status = None
        self.openTime = None
        self.currTime = None

    def garage_close(self):
        GPIO.setmode(GPIO.BCM)
        garage_pin = 4
        GPIO.setup(garage_pin, GPIO.OUT)
        GPIO.output(garage_pin, 0)
        time.sleep(5)
        GPIO.output(garage_pin, 1)
        time.sleep(5)
        GPIO.cleanup()

    def id_class_name(self, class_id, classes):  
        for key, value in classes.items():
            if class_id == key:
                return value
    
    def garage_door(self, frame):
        self.model.setInput(cv2.dnn.blobFromImage(frame, size=(64, 64), swapRB=True))
        output = self.model.forward()
        # If no object tracking try detection
        garage_status = None
        
        if np.argmax(output) == 1:
            garage_status = "garage open"
            if self.status == "garage closed":
                self.openTime = time.time()
            self.status = garage_status
        else:
            garage_status = "garage closed"
            self.status = garage_status

        self.currTime = time.time()
        
        if self.openTime is not None:
            openTime = int(self.currTime - self.openTime)
            print("openTime:", openTime)

            # if (openTime > 300):
            if (openTime > 120):
                self.garage_close()
                # reset open time
                self.openTime = None

        return garage_status
