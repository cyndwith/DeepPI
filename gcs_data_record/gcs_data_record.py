# Goolge client storage - client
from gcs_client import *
import os
import time
import cv2

camera = cv2.VideoCapture(0)
time.sleep(2.0)

gcs_client = GCSClient()

num_images = 1000

i = 1

while (i < num_images):
    
    grabbed, frame = camera.read()

    frame = cv2.resize(frame, (300,300))

    if not grabbed:
        break
    
    filePath = os.getcwd()
    fileName = f'image_{i}.jpg'
    localFile = filePath + gcs_client.local_folder + fileName
    print(fileName)
    cv2.imwrite(localFile, frame)
    
    gcsFile = localFile # gcs_client.local_folder + fileName
    gcs_client.upload_file(gcsFile)

    key = cv2.waitKey(1) & 0xFF
    i = i + 2
    if key == ord("q"):
        break
   
