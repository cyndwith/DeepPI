# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2

class ObjectDetection:
    def __init__(self):
        self.classNames = { 0: 'background', 1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
                            7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
                           13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
                           18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
                           24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
                           32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
                           37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
                           41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
                           46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
                           51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
                           56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
                           61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
                           67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
                           75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
                           80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
                           86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}
        # load the model
        self.model = cv2.dnn.readNetFromTensorflow('models/frozen_inference_graph.pb',
                                                   'models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        # object BBox
        self.objBBox = None
    def id_class_name(self, class_id, classes):  
        for key, value in classes.items():
            if class_id == key:
                return value

    def object_detection(self, frame, frameCenter):
        self.model.setInput(cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True))
        output = self.model.forward()
        frame_width, frame_height = 300, 300
        # tracking
        tracker = cv2.TrackerMOSSE_create()
        if self.objBBox is not None:
            # new bounding box, returns 0 if it fails
            (success, box) = tracker.update(frame)
            print(box)
            print("Tracking Status:", success)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + w), (0, 255, 0), 2)

            info = [("Tracker", "MOSSE"),
                    ("Success", "Yes" if success else "No"),
                    ]
            H = 150
            W = 150
            # loop over the info tuples and draw them on frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if success:
                objX = x + (w // 2)
                objY = y + (h // 2)

                objCenter = (objX, objY)
                objBBox = (box_x, box_y, box_width, box_height)
                self.objBBox = objBBox
                return (objCenter, objBBox)
        
        # If no object tracking try detection
        for detection in output[0, 0, :, :]:
            confidence = detection[2]
            if confidence > .5:
                class_id = detection[1]
                class_name = self.id_class_name(class_id, self.classNames)
                print(str(str(class_id) + " " + str(detection[2]) + " " + class_name))
                if 'person' in class_name:
                    box_x = detection[3] * frame_width
                    box_y = detection[4] * frame_height
                    box_width = detection[5] * frame_width
                    box_height = detection[6] * frame_height
                    cv2.rectangle(frame, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (23, 230, 210),
                                  thickness=1)
                    cv2.putText(frame, class_name, (int(box_x), int(box_y + .05 * frame_height)), cv2.FONT_HERSHEY_SIMPLEX,
                                (.005 * frame_width), (0, 0, 255))

                    objX = box_x + (box_width // 2)
                    objY = box_y + (box_height // 2)

                    objCenter = (objX, objY)
                    objBBox = (box_x, box_y, box_width, box_height)
                    self.objBBox = objBBox
                    # Initialize the tracker
                    tracker.init(frame, objBBox)

                    print("objCenter:", objCenter)
                    return (objCenter, objBBox)
 
        return (frameCenter, None)
