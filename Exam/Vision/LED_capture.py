# tracking.py
# Created by Michael Marek (2016)
# Track the position of tennis balls in a webcam video feed.
#!/usr/bin/python3
import cv2
import numpy as np
import subprocess
import tempfile
import os
import random
from Models import Colors

width = 640
height = 480

def get_keypoints(color):
  tmpname = tempfile.mkstemp(suffix='.png')[1]
  # capture image with raspistill built in
  raspistill = ['/opt/vc/bin/raspistill','-w', str(width),'-h', str(height),'-t','1','-ss', '4000','--nopreview','-ex', 'spotlight', '-vf', '-hf', '-o',tmpname]
  try:
    subprocess.check_call(raspistill)
  except Exception as e:
    print("error taking photo")
    return []

  frame = cv2.imread(tmpname)[170:,:] #crop to 640x290 and taking the bottom part
  keypoints = process(frame, color)
  os.remove(tmpname)

  return keypoints

def main():
  # Just for standalone testing. Not used in the actual program.
  tmpname = tempfile.mkstemp(suffix='.png')[1]
  # capture image with raspistill built in
  raspistill = ['/opt/vc/bin/raspistill','-w', str(width),'-h', str(height),'-ex', 'spotlight', '--nopreview', '-t','1', '-ss', '4000', '-vf', '-hf', '-o',tmpname]
  try:
    subprocess.check_call(raspistill)
  except Exception as e:
    print("error taking photo")
    return []

  frame = cv2.imread(tmpname)[170:,:] #crop to 640x310 and taking the bottom part
  
  keypoints = process(frame, Colors.RedOrange)
  for keypoint in keypoints:
    cv2.circle(frame, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
 
  cv2.imwrite("./pics/led_capture_test_" + str(random.random()) + ".png", frame)
  os.remove(tmpname)
  return

def process(frame, color):
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
  if color == Colors.RedOrange:
    first_lower = (0, 25, 50)
    first_upper = (30, 255, 255)
    second_lower = (170, 25, 50)
    second_upper = (180, 255, 255)
  elif color == Colors.Green:
    lower = (45, 30, 50)
    upper = (90, 255, 255)
  elif color == Colors.Blue:
    lower = (90, 50, 100)
    upper = (125, 255, 255)
  else: # This is Purple, but we dont rly need this because we dont care about purple
    lower = (135, 50, 200)
    upper = (150, 255, 255)

  if color == "redorange":
    mask1 = cv2.inRange(hsv, first_lower, first_upper)
    mask2 = cv2.inRange(hsv, second_lower, second_upper)
    color_filter = cv2.bitwise_or(mask1, mask2)
  else:
    color_filter = cv2.inRange(hsv, lower, upper)
  
  thresh = cv2.threshold(color_filter, 60, 255, cv2.THRESH_BINARY)[1]

  params = cv2.SimpleBlobDetector_Params()
  params.blobColor = 255 #blobs are binary
  #no filters
  params.filterByArea = False
  params.filterByCircularity = False
  params.filterByConvexity = False
  params.filterByInertia = False

  detector = cv2.SimpleBlobDetector_create(params)

  keypoints = list(detector.detect(thresh))
  keypoints.sort(key=lambda point: point.size)

  #print("keypoint amount: " + str(len(keypoints)))
  return keypoints

if __name__ == "__main__":
  main()