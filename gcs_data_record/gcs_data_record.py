# Goolge client storage - client
from gcs_client import *
import os
import time
import cv2

camera = cv2.VideoCapture(0)
time.sleep(2.0)

gcs_client = GCSClient()

i = 0
while (i < 10):
    
    grabbed, frame = camera.read()

    frame = cv2.resize(frame, (300,300))

    if not grabbed:
        break
    
    filePath = os.getcwd()
    fileName = f'image_{i}.jpg'
    localFile = filePath + '/../' + gcs_client.local_folder + fileName
    print(fileName)
    cv2.imwrite(localFile, frame)
    
    gcsFile = gcs_client.local_folder + fileName
    gcs_client.upload_file(gcsFile)

    key = cv2.waitKey(1) & 0xFF
    i = i + 1
    if key == ord("q"):
        break
   
