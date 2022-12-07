# tracking.py
# Created by Michael Marek (2016)
# Track the position of tennis balls in a webcam video feed.

import cv2
import numpy as np
import subprocess
import tempfile
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from Models import Colors

width = 640
height = 480
camera = PiCamera()
camera.resolution = (width, height)
camera.exposure_mode = 'spotlight'
rawCapture = PiRGBArray(camera, size=(width, height))

def get_keypoints(color):
  camera.capture(rawCapture, format="bgr")
  
  frame = rawCapture.array
  frame = cv2.rotate(frame, cv2.ROTATE_180)
  frame = frame[170:,:] #crop to 640x290 and taking the bottom part
  keypoints = process(frame, color)

  rawCapture.truncate(0) # flush camera buffer
  return keypoints

def main():
  camera.capture(rawCapture, format="bgr")
  
  frame = rawCapture.array
  frame = cv2.rotate(frame, cv2.ROTATE_180)
  frame = frame[170:,:] #crop to 640x290 and taking the bottom part

  keypoints = process(frame, Colors.RedOrange)
  for keypoint in keypoints:
    #cv2.circle(mask, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
    cv2.circle(frame, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
      #mean = cv2.mean(frame,mask=mask)
 
  cv2.imwrite("./pics/led_capture_test.png", frame)
  rawCapture.truncate(0) # flush camera buffer
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
  elif color == Colors.Purple: # we dont rly need this because we dont care 
    lower = (135, 50, 200)
    upper = (150, 255, 255)
  else: # old red
    lower = (170,25,0)
    upper = (205,255,255)
  #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  
  if color == "redorange":
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
  main()