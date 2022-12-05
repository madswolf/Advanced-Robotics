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
roi_params = "1,0.4,1,1"
camera = PiCamera()
camera.resolution = (width, height)
camera.exposure_mode = 'spotlight'
rawCapture = PiRGBArray(camera, size=(width, height))

def get_keypoints(color):
  camera.capture(rawCapture, format="bgr")
  
  frame = rawCapture.array
  frame = cv2.rotate(frame, cv2.ROTATE_180)
  frame = frame[190:,:] #crop to 640x290 and taking the bottom part
  keypoints = process(frame, color)

  rawCapture.truncate(0) # flush camera buffer
  return keypoints

def main():
  camera.capture(rawCapture, format="bgr")
  
  frame = rawCapture.array
  frame = cv2.rotate(frame, cv2.ROTATE_180)
  frame = frame[190:,:] #crop to 640x290 and taking the bottom part

  keypoints = process(frame, "red")
  for keypoint in keypoints:
    #cv2.circle(mask, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
    cv2.circle(frame, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size/2), (255,255,255), -1)
      #mean = cv2.mean(frame,mask=mask)
 
  cv2.imwrite("./pics/led_capture_test.png", frame)
  rawCapture.truncate(0) # flush camera buffer
  return

def process(frame, color):
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
  if color == Colors.Red: # this is also covering orange
    lower = (0, 75, 170)
    upper = (20, 255, 255)
  elif color == Colors.Green:
    lower = (45, 50, 200)
    upper = (90, 255, 255)
  elif color == Colors.Blue:
    lower = (90, 50, 200)
    upper = (115, 255, 255)
  elif color == Colors.Purple: # we dont rly need this because we dont care 
    lower = (135, 50, 200)
    upper = (150, 255, 255)
  else: # old red
    lower = (170,25,0)
    upper = (205,255,255)
  
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