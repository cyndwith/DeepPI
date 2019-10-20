# Goolge client storage - client
from google.cloud import storage
from os import listdir
from os.path import isfile, join
from random import randint

import os
import cv2
import google.auth

# Google Cloud Storage
# export GOOGLE_APPLICATION_CREDENTIALS=DeepPI-<number>.json
credential, project = google.auth.default()
print("credential:", credential)
print("project:", project)

#client = storage.Client()
#bucket = client.get_bucket('garage_door')
image = cv2.imread('image.jpg')

bucketFolder = "DeepPI/garage_door/"
localFolder = "DeepPI_data/garage_door/"

class GCSClient:
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket('garage_door')
        self.bucket_folder = "DeepPI/garage_door/"
        self.local_folder = "/../DeepPI_data/garage_door/"

    def upload_files(self, localFolder):
        """Upload files to GCP bucket."""
        files = [f for f in listdir(self.local_folder) if isfile(join(self.local_folder, f))]
        for file in files:
            localFile = self.local_folder + file
            print("uploading file... ", localFile)
            blob = self.bucket.blob(self.bucket_folder + file)
            blob.upload_from_filename(localFile)
        return f'Uploaded {files} to "{self.bucket}" bucket.'

    def upload_file(self, localFile):
        """Uploading file to GCP bucket"""
        print("uploading file...", localFile)
        fileName = os.path.basename(localFile)
        blob = self.bucket.blob(self.bucket_folder + fileName)
        blob.upload_from_filename(localFile)
        return f'Uploaded {localFile} to "{self.bucket}" bucket.'
    
    def list_files(self):
        """List all files in GCP bucket."""
        files = self.bucket.list_blobs(prefix=self.bucket_folder)
        fileList = [file.name for file in files if '.' in file.name]
        return fileList


    def download_random_file(self):
        """Download random file from GCP bucket."""
        fileList = list_files(self.bucket)
        rand = randint(0, len(fileList) - 1)
        blob = self.bucket.blob(fileList[rand])
        fileName = blob.name.split('/')[-1]
        blob.download_to_filename(self.local_folder + fileName)
        return f'{fileName} downloaded from bucket.'

    def delete_file(self, fileName):
        """Delete file from GCP bucket."""
        self.bucket.delete_blob(self.bucket_folder + fileName)
        return f'{fileName} deleted from bucket.'

    def rename_file(self, fileName, newFileName):
        """Rename file in GCP bucket."""
        blob = self.bucket.blob(self.bucket_folder + fileName)
        self.bucket.rename_blob(blob, new_name=newFileName)
        return f'{fileName} renamed to {newFileName}.'

