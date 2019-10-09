from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from object_detection import ObjectDetection
from pid import *
from servos_control import *
import argparse
import signal
import time
import sys
import cv2

# servo range for the steering control
servoRange = (-30, 30)

# function to handle keyboard interrupt
def signal_handler(sig, frame):
    # print a status message
    print("[INFO] You pressed `ctrl + c`! Exiting...")
    GPIO.cleanup()
    # exit
    sys.exit()

def obj_detection(objX, objY, centerX, centerY):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

    # Loading model
    obj = ObjectDetection()
    # loop indefinitely
    while True:
        # grab the frame from the threaded video stream and flip it
	# vertically (since our camera was upside down)
        grabbed, frame = camera.read()
        # frame = cv2.flip(frame, 0)
        frame = cv2.resize(frame, (150, 150))
        if not grabbed:
            break

	# calculate the center of the frame as this is where we will
	# try to keep the object
        (H, W) = frame.shape[:2]
        centerX.value = W // 2
        centerY.value = H // 2

	# find the object's location
        objectLoc = obj.object_detection(frame, (centerX.value, centerY.value))
        ((objX.value, objY.value), rect) = objectLoc
	# extract the bounding box and draw it
        if rect is not None:
            (x, y, w, h) = rect
            cv2.rectangle(frame, (int(x), int(y)), (int(w), int(h)), (0, 255, 0), 2)

	# display the frame to the screen
        cv2.imshow("Person Tracking", frame)
        cv2.waitKey(1)

def pid_process(output, p, i, d, objCoord, centerCoord):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    # create a PID and initialize it
    p = PID(p.value, i.value, d.value)
    p.initialize()

    # loop indefinitely
    while True:
        # calculate the error
        error = centerCoord.value - objCoord.value
	# update the value
        output.value = p.update(error)

def set_servos(angle, servosCtrl):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)
    # loop indefinitely
    while True:
        # steer angles are reversed ? steerAngle = -1 * angle.value
        steerAngle = angle.value // 2
        print("steerAngle:", steerAngle)
        servosCtrl.steer_to_angle(steerAngle)


if __name__ == "__main__":
    print("main called\n")
    # start a manager for managing process-safe variables
    with Manager() as manager:
        print("Manager() called\n")
        # enable the servos
        # set integer values for the object center (x, y)-coordinates
        centerX = manager.Value("i", 0)
        centerY = manager.Value("i", 0)
    	# set integer values for the object's (x, y)-coordinates
        objX = manager.Value("i", 0)
        objY = manager.Value("i", 0)
	# pan and tilt values will be managed by independed PIDs
        servosCtrl = ServosControl()
        steerAngle = manager.Value("i", 0)
	# set PID values for panning
        angleP = manager.Value("f", 0.09)
        angleI = manager.Value("f", 0.08)
        angleD = manager.Value("f", 0.002)
	# we have 4 independent processes
	# 1. objectCenter    - finds/localizes the object
	# 2. steer Angle     - PID control loop determines steer angle
	# 3. Servos Control  - drives the servos to proper angles based
	#                      on PID feedback to keep object in center
        processObjectDetection = Process(target=obj_detection, args=(objX, objY, centerX, centerY))
        processSteerAngle      = Process(target=pid_process, args=(steerAngle, angleP, angleI, angleD, objX, centerX))
        processServosControl   = Process(target=set_servos, args=(steerAngle, servosCtrl))
        # start all 3 processes
        processObjectDetection.start()
        processSteerAngle.start()
        processServosControl.start()
	# join all 4 processes
        processObjectDetection.join()
        processSteerAngle.join()
        processServosControl.join()
	# disable the servos
        servosCtrl.disable()

