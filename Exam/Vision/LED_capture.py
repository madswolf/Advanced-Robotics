# tracking.py
# Created by Michael Marek (2016)
# Track the position of tennis balls in a webcam video feed.

import cv2
import numpy as np
import subprocess
import tempfile
import os
import random
import string
from Models import Colors

width = 640
height = 480

def get_keypoints(color):
  tmpname = tempfile.mkstemp(suffix='.png')[1]
  # capture image with raspistill built in
  raspistill = ['/opt/vc/bin/raspistill','-w', str(width),'-h', str(height),'-t','1','-ss', '4000','-ex', 'spotlight', '-vf', '-hf', '-o',tmpname]
  try:
    subprocess.check_call(raspistill)
  except Exception as e:
    print("error taking photo")
    return [None]

  frame = cv2.imread(tmpname)[190:,:] #crop to 640x290 and taking the bottom part
  keypoints = process(frame, color)
  os.remove(tmpname)

  return keypoints

def main():
  tmpname = tempfile.mkstemp(suffix='.png')[1]
  # capture image with raspistill built in
  raspistill = ['/opt/vc/bin/raspistill','-w', str(width),'-h', str(height),'-t','1','-ss', '4000','-ex', 'spotlight', '-vf', '-hf', '-o',tmpname]
  try:
    subprocess.check_call(raspistill)
  except Exception as e:
    print("error taking photo")
    return 1

  frame = cv2.imread(tmpname)[190:,:] #crop to 640x290 and taking the bottom part
  

  keypoints = process(frame, "red")
  for keypoint in keypoints:
    #cv2.circle(mask, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
    cv2.circle(frame, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
      #mean = cv2.mean(frame,mask=mask)
 
  cv2.imwrite("./pics/led_capture_test.png", frame)

  os.remove(tmpname)
  return

def process(frame, color):
  """
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  # tennis ball colour range
  lower = (20, 100, 100)
  upper = (70, 255, 255)

  # you can also track, uhh, lemons with this colour range
  # lower = (10, 100, 100)
  # upper = (40, 255, 255)

  mask = cv2.inRange(hsv, lower, upper)
  # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, None)
  mask = cv2.GaussianBlur(mask, (5,5), 2)
  mask = cv2.erode(mask, np.ones((6,6), dtype=np.uint8), iterations=2)
  mask = cv2.dilate(mask, None, iterations=2)

  contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


  circles = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)
  bestCircle = (0, (0,0))
  for contour in contours:
      (x, y), radius = cv2.minEnclosingCircle(contour)
      center = (int(x), int(y))
      radius = int(radius)
      if(radius > bestCircle[0]):
          bestCircle = (radius, center)

  cv2.circle(circles, bestCircle[1], bestCircle[0], (0, 255, 0), 2) # tennis ball outline
  cv2.circle(circles, bestCircle[1], 1, (0, 0, 255), 2)      # tennis ball centroid

  masked = cv2.bitwise_and(frame,frame, mask=mask)
  result = cv2.addWeighted(frame, 1, circles, 1, 0)
  """
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
  if color == Colors.Green:
    lower = (20, 25, 50)
    upper = (70, 255, 255)
  elif color == Colors.Orange:
    lower = (10, 25, 50)
    upper = (40, 255, 255)
  elif color == Colors.Red:
    first_lower = (0, 25, 50)
    first_upper = (10, 255, 255)
    second_lower = (170, 25, 50)
    second_upper = (180, 255, 255)
  elif color == Colors.Blue:
    lower = (110, 25, 50)
    upper = (130, 255, 255)
  else: # old red
    lower = (170,25,0)
    upper = (205,255,255)

  if color == Colors.Red:
    mask1 = cv2.inRange(hsv, first_lower, first_upper)
    mask2 = cv2.inRange(hsv, second_lower, second_upper)
    color_filter = cv2.bitwise_or(mask1, mask2)
  else:
    color_filter = cv2.inRange(hsv, lower, upper)
  #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  
  thresh = cv2.threshold(color_filter, 60, 255, cv2.THRESH_BINARY)[1]

  params = cv2.SimpleBlobDetector_Params()
  params.blobColor = 255 #blobs are binary
  #no filters
  params.filterByArea = False
  params.filterByCircularity = False
  params.filterByConvexity = False
  params.filterByInertia = False

  detector = cv2.SimpleBlobDetector_create(params)

  keypoints = detector.detect(thresh)
  keypoints = [point for point in keypoints if point.size > 1.85 ]

  #height,width,depth = frame.shape
  print("keypoint amount: " + str(len(keypoints)))
  #mask = np.zeros((height,width), np.uint8)
  return keypoints

if __name__ == "__main__":
  get_keypoints(Colors.Red)