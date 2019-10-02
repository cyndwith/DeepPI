# import the necessary packages
# from imutils.video import VideoStream
# from imutils.video import FPS
import argparse
import imutils
import time
import cv2

# Different types for trackers
# 1. CSRT : cv2.TrackerCSRT_create
# 2. KCF : cv2.TrackerKCF_create
# 3. boosting: cv2.TrackerBoosting_create
# 4. MIL : cv2.TrackerMIL_create
# 5. TLD : cv2.TrackerTLD_create
# 6. Medianflow : cv2.TrackerMedianFlow_create
# 7. MOSSE : cv2.TrackerMOSSE_create
# 8. GOTURN: Deeplearning based tracking
# Note: Caffe model downloaded and saved in same folder
# Model link: https://github.com/spmallick/goturn-files
tracker = cv2.TrackerMOSSE_create()
# tracker = cv2.TrackerGOTURN_create()
initBBox = None

#camera = cv2.VideoCapture(0)
video = cv2.VideoCapture("dashcam_boston.mp4")
time.sleep(0.25)

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    
    #(grabbed, frame) = camera.read()
    (grabbed, frame) = video.read()
    # if the frame could not be grabbed, then we have reached the end of the video
    #    if not grabbed:
    #    break
    if frame is None:
        break

    print("frame shape:", frame.shape[:2])
    W, H = frame.shape[:2]
    text = "No Detection"

    # resize the frame
    frame = cv2.resize(frame, (300, 300))


    # check to see if we are currently tracking an object
    if initBBox is not None:
        # grab the new bounding box coordinates of the object
        # return's 0 on failure
        (success, box) = tracker.update(frame)
        print(box)
        print(success)
        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # update the FPS counter
        # fps.update()
        # fps.stop()

        # initialize the set of information we'll be displaying on
        # the frame
        info = [
            ("Tracker", "MOSSE"),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(x)),
        ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # show the frame and record if the user presses a key
    cv2.imshow("Camera Feed", frame)
    cv2.imwrite("output.jpg", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key is pressed, break from the lop
    if key == ord("s"):
        initBBox = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, initBBox)
        # fps = FPS().start()
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
