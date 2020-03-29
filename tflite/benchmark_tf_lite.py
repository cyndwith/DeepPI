import tensorflow as tf

import sys
import os
import logging as log
import argparse
import subprocess
from timeit import default_timer as timer

import cv2
import numpy as np

from PIL import Image
from PIL import ImageFont, ImageDraw

# Function to draw a rectangle with width > 1
def draw_rectangle(draw, coordinates, color, width=1):
    for i in range(width):
        rect_start = (coordinates[0] - i, coordinates[1] - i)
        rect_end = (coordinates[2] + i, coordinates[3] + i)
        draw.rectangle((rect_start, rect_end), outline = color, fill = color)

# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

# Function for detection post processing
def detection_post_processing(interpreter, labels, image):
   img = Image.open(image);
   draw = ImageDraw.Draw(img, 'RGBA')
   picture = cv2.imread(image)
   initial_h, initial_w, channels = picture.shape
   output_details = interpreter.get_output_details()
   
   detected_boxes = interpreter.get_tensor(output_details[0]['index'])
   detected_classes = interpreter.get_tensor(output_details[1]['index'])
   detected_scores = interpreter.get_tensor(output_details[2]['index'])
   num_boxes = interpreter.get_tensor(output_details[3]['index'])
   
   for i in range(int(num_boxes)):
      top, left, bottom, right = detected_boxes[0][i]
      classId = int(detected_classes[0][i])
      score = detected_scores[0][i]
      if score > 0.3:
          xmin = left * initial_w
          ymin = bottom * initial_h
          xmax = right * initial_w
          ymax = top * initial_h
          if labels:
              print(labels[classId], 'score = ', score)
          else:
              print ('score = ', score)
          box = [xmin, ymin, xmax, ymax]
          draw_rectangle(draw, box, (0,128,128,20), width=5)
          if labels:
             draw.text((box[0] + 20, box[1] + 20), labels[classId], fill=(255,255,255,20)) #, font=helvetica)
   output = 'detection_output.jpeg'
   img.save(output)
   print ('Saved to ', output)

def classification_post_processing(interpreter, labels, image):
    img = Image.open(image)
    draw = ImageDraw.Draw(img, 'RGBA')
    picture = cv2.imread(image)
    initial_h, initial_w, channels = picture.shape
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 72)

    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
    print(output)
    # if quantized , dequantize the output
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)
    ordered = np.argpartition(-output, 1)
    classId = int(ordered[:1])
    if labels:
        print("image label: ", labels[classId])
        draw.text((initial_w/2 - 100, initial_h - 100), labels[classId], font=fnt, fill=(255,0,0,0))
    output = 'classification/classification_output.jpg'
    img.save(output)
    print('Saved to ', output)


def segmentation_post_processing(interpreter, labels, image):
    img = Image.open(image)
    draw = ImageDraw.Draw(img, 'RGBA')
    picture = cv2.imread(image)
    initial_h, initial_w, channels = picture.shape
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 72)

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()[0]
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    frame = cv2.resize(picture, (width, height))
    print(output_details)
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
    print("output.shape:", output.shape)
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)
    ordered = np.argpartition(-output, 1, axis=2)
    print("ordered.shape:", ordered.shape)
    argmax  = np.squeeze(ordered[:, :, :1])
    print("argmax.shape:", argmax.shape)
    print(argmax)
    print("labels", labels) 
    for idx, class_name in labels.items():
        print("idx, class_name:", idx, class_name)
        if idx in argmax:
            print("class:", class_name," is present in image")
    
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
    print(colored_mask.shape)
    for idx, class_name in labels.items():
        colored_mask[argmax == idx,:] = color_mask[class_name]
    print(colored_mask.shape)
    colored_mask = cv2.resize(colored_mask, (initial_w, initial_h))
    output = 'segmentation/segmentation_output.jpeg'
    img.save(output)
    mask_frame = picture*0.5 + colored_mask*0.5
    cv2.imwrite(output, mask_frame)
    print('Saved to ', output)

def output_post_processing(network_type, interpreter, labels, img):
    print("network_type:", network_type)
    if network_type == 'detection':
        detection_post_processing(interpreter, labels, img)
    elif network_type == 'classification':
        classification_post_processing(interpreter, labels, img)
    elif network_type == 'segmentation':
        segmentation_post_processing(interpreter, labels, img)
    elif network_type == 'benchmark':
        pass
    print("Finished Output Post Processing\n")

def inference_tf(runs, image, model, output, network_type, label = None):
   if label:
       labels = ReadLabelFile(label)
   else:
       labels = None
   
   # Load TFLite model and allocate tensors.
   interpreter = tf.lite.Interpreter(model_path=model)
   interpreter.allocate_tensors()
   
   # Get input and output tensors.
   input_details = interpreter.get_input_details()
   output_details = interpreter.get_output_details()
   height = input_details[0]['shape'][1]
   width = input_details[0]['shape'][2]
   floating_model = False
   if input_details[0]['dtype'] == np.float32:
       floating_model = True
   
   img = Image.open(image)
   draw = ImageDraw.Draw(img, 'RGBA')
   #helvetica=ImageFont.truetype("arial.ttf", size=72)
   #helvetica=ImageFont.truetype("./Helvetica.ttf", size=72)
        
   picture = cv2.imread(image)
   initial_h, initial_w, channels = picture.shape
   frame = cv2.resize(picture, (width, height))
   
   # add N dim
   input_data = np.expand_dims(frame, axis=0)
   
   if floating_model:
      input_data = (np.float32(input_data) - 127.5) / 127.5
   
   interpreter.set_num_threads(4)
   interpreter.set_tensor(input_details[0]['index'], input_data)
   
   #  Start synchronous inference and get inference result
   # Run inference.
   print("Running inferencing for ", runs, " times.")
       
   if runs == 1:
      start = timer()
      interpreter.invoke()
      end = timer()
      print('Elapsed time is ', ((end - start)/runs)*1000, 'ms' )
   else:
      start = timer()
      print('Initial run, discarding.')
      interpreter.invoke()
      end = timer()
      print('First run time is ', (end - start)*1000, 'ms')
      start = timer()
      for i in range(runs):
         interpreter.invoke()
      end = timer()
      print('Elapsed time is ', ((end - start)/runs)*1000, 'ms' )
    
   output_post_processing(network_type, interpreter, labels, image)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Path of the detection model.', required=True)
    parser.add_argument('--label', help='Path of the labels file.')
    parser.add_argument('--input', help='File path of the input image.', required=True)
    parser.add_argument('--output', help='File path of the output image.')
    parser.add_argument('--runs', help='Number of times to run the inference', type=int, default=1)
    parser.add_argument('--network_type', help='classification/detection/segmentation/benchmark network', default='classification')
    args = parser.parse_args()
    
    if ( args.output):
      output_file = args.output
    else:
      output_file = 'out.jpg'
    
    if ( args.label ):
      label_file = args.label
    else:
      label_file = None
    
    result = inference_tf( args.runs, args.input, args.model, output_file, args.network_type, label_file)

if __name__ == '__main__':
  main()
