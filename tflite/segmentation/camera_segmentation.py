"""Example using TF Lite for image segmentation with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import time
import numpy as np
import picamera
import cv2

from PIL import Image
from tflite_runtime.interpreter import Interpreter

# Function to read labels from text files.
def load_labels(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def image_segmentation(interpreter, labels, image, top_k=1):
  """Returns a segemented image array  results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, 1, axis=2)
  labled_image = np.squeeze(ordered[:, :, :1])
    
  image_labels = []
  for idx, class_name in labels.items():
    if idx in labled_image:
        image_labels.append([idx, class_name])
  
  return image_labels

def segmentation_post_processing(interpreter, labels, image):
    #initial_h, initial_w, channels = image.shape
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()[0]
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    frame_bytes = np.frombuffer(image.tobytes(), dtype=np.uint8)
    #frame_bytes = np.fromstring(image.tobytes(), dtype=np.uint8)
    frame = frame_bytes.reshape((width, height, 3)) #cv2.resize(image, (width, height))
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)
    ordered = np.argpartition(-output, 1, axis=2)
    argmax  = np.squeeze(ordered[:, :, :1])
    '''
    for idx, class_name in labels.items():
        if idx in argmax:
            print("class:", class_name," is present in image")
    '''
    #define color mask for classes
    color_mask = {'background':(0,0,0), #black
                  'aeroplane':(0,0,255),#blue
                  'bicycle':(94,31,31), #brown
                  'bird':(31,94,35),    #green
                  'boat':(13,169,236),  #light blue
                  'bottle':(23, 122, 165), #sea blue
                  'bus':(165, 23,56),      #red
                  'car':(246, 101, 29),    #orange
                  'cat':(237,15,245),      #pink
                  'chair':(137,15,245),    #purple
                  'cow':(255,255,255),     #white
                  'dinningtable':(229,245,15),  #yellow
                  'dog':(115,115,109),     #gray
                  'horse':(109, 115, 115), #horse
                  'motorbike':(26,48,245), #dark blue
                  'person':(26,245,245),   #light blue
                  'pottedplant':(26,245,40), #light green
                  'sheep':(115,115,109),     #gray
                  'sofa':(238,87,12),      #orange
                  'train':(255, 0, 0),     #red
                  'tvmonitor':(12,238,222) }  #light blue
    
    colored_mask = np.zeros(frame.shape)
    for idx, class_name in labels.items():
        colored_mask[argmax == idx,:] = color_mask[class_name]
    #colored_mask = cv2.resize(colored_mask, (initial_w, initial_h))
    output = 'mask_output.jpeg'
    mask_frame = frame*0.5 + colored_mask*0.5
    mask_frame = cv2.resize(mask_frame, (640, 480))
    cv2.imwrite(output, mask_frame)
    print('Saved to ', output)
    return mask_frame


def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  args = parser.parse_args()

  labels = load_labels(args.labels)

  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  input_details = interpreter.get_input_details()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']

  if input_details[0]['dtype'] == np.float32:
    floating_model = True

  with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
    camera.start_preview()
    try:
      stream = io.BytesIO()
      loop = 0
      over_lay =  0
      for _ in camera.capture_continuous(
          stream, format='jpeg', use_video_port=True):
        stream.seek(0)
        image = Image.open(stream).convert('RGB').resize((width, height),
                                                         Image.ANTIALIAS)
        frame_bytes = np.frombuffer(image.tobytes(), dtype=np.uint8)
        #frame_bytes = np.fromstring(image.tobytes(), dtype=np.uint8)
        frame = frame_bytes.reshape((width, height, 3)) 
        input_data = np.expand_dims(frame, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - 127.5) / 127.5

        start_time = time.time()
        image_labels = image_segmentation(interpreter, labels, input_data)
        elapsed_ms = (time.time() - start_time) * 1000
        mask_frame = segmentation_post_processing(interpreter, labels, image)
        mask_frame = cv2.resize(mask_frame, (480, 640))
        if (loop % 1 == 0): # Update overlay every 10 frames
            if (over_lay == 1): #clear last over_lay
                camera.remove_overlay(o)
            img = Image.open('mask_output.jpeg')
            # Create an image padded to the required size with
            # mode 'RGB'
            pad = Image.new('RGB', (
                  ((img.size[0] + 31) // 32) * 32,
                  ((img.size[1] + 15) // 16) * 16,
                  ))
            # Paste the original image into the padded one
            pad.paste(img, (0, 0))

            # Add the overlay with the padded image as the source,
            # but the original image's dimensions
            o = camera.add_overlay(pad.tobytes(), size=img.size)
            o.alpha = 128
            o.layer = 3
            over_lay = 1
        stream.seek(0)
        stream.truncate()

        print_label = ''
        for idx, class_name in image_labels: 
            print_label = print_label + ', ' + class_name
        camera.annotate_text = '%s \n%.1fms' % (print_label, elapsed_ms)
        loop += 1
    finally:
      camera.stop_preview()


if __name__ == '__main__':
  main()
