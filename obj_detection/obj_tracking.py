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

camera = cv2.VideoCapture(0)
time.sleep(0.25)

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    print("frame shape:", frame.shape[:2])
    frame_width, frame_height = frame.shape[:2]
    text = "No Detection"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame
    frame = imutils.resize(frame, (300, 300), cv2.INTER_LINEAR)
    (frame_width, frame_height) = (300, 300)

    # resize frame to (300, 300)
    model.setInput(cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True))

    output = model.forward()
    # print(output[0,0,:,:].shape)

    for detection in output[0, 0, :, :]:
        confidence = detection[2]
        if confidence > .5:
            class_id = detection[1]
            class_name = id_class_name(class_id, classNames)
            # detect and track people
            if "person" in class_name:
                print(str(str(class_id) + " " + str(detection[2]) + " " + class_name))
                box_x = detection[3] * frame_width
                box_y = detection[4] * frame_height
                box_width = detection[5] * frame_width
                box_height = detection[6] * frame_height
                cv2.rectangle(frame, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (23, 230, 210),
                              thickness=1)
                cv2.putText(frame, class_name, (int(box_x), int(box_y + .05 * frame_height)), cv2.FONT_HERSHEY_SIMPLEX,
                            (.005 * frame_width), (0, 0, 255))

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Tracker Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Camera Feed", frame)
    cv2.imwrite("output.jpg", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("s"):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, initBB)
        # fps = FPS().start()
    if key == ord("q"):
        break

    # check to see if we are currently tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates of the object
        # return's 0 on failure
        (success, box) = tracker.update(frame)

        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

        # update the FPS counter
        # fps.update()
        # fps.stop()

        # initialize the set of information we'll be displaying on
        # the frame
        info = [
            ("Tracker", "MOSSE"),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()