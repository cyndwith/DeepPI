# import the necessary packages
# from imutils.video import VideoStream
# from imutils.video import FPS

import argparse
import imutils
import time
import cv2

from garage_door import *

camera = cv2.VideoCapture(0)
#video = cv2.VideoCapture("dashcam_boston.mp4")
time.sleep(0.5)

obj = GarageDoor()
# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied 
    (grabbed, frame) = camera.read()
    
    # if the frame could not be grabbed, then we have reached the end of the video
    if not grabbed:
        print("grabbed:", grabbed)
        break

    # resize the frame
    frame = cv2.resize(frame, (64,64))

    garage_status = obj.garage_door(frame)
    print("garage status:", garage_status)
    
    # show the frame and record if the user presses a key
    cv2.imshow("Camera Feed", frame)
    cv2.imwrite("output.jpg", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        print("'q' is pressed, break from the loop\n")
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
