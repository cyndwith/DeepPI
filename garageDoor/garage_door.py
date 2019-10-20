# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np

class GarageDoor:
    def __init__(self):
        print("GarageDoor\n")
        self.classNames = { 0: 'closed', 1: 'open'}
        # load the model
        print("read the model\n")
        # self.model = cv2.dnn.readNetFromTensorflow('myGarage.pb', 'myGarage.pbtxt')
        self.model = cv2.dnn.readNetFromTensorflow('myGarage.pb')
        # object BBox
        self.status = None
    
    def id_class_name(self, class_id, classes):  
        for key, value in classes.items():
            if class_id == key:
                return value
    
    def garage_door(self, frame):
        self.model.setInput(cv2.dnn.blobFromImage(frame, size=(64, 64), swapRB=True))
        output = self.model.forward()
        print("output:", output)
        # If no object tracking try detection
        garage_status = None
        
        if np.argmax(output) == 1:
            garage_status = "garage open"
        else:
            garage_status = "garage closed"

        return garage_status
