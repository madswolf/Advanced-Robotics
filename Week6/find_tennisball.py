# tracking.py
# Created by Michael Marek (2016)
# Track the position of tennis balls in a webcam video feed.
from turtle import width
from picamera import PiCamera
import cv2
import numpy as np

camera = PiCamera()

width = 640
height = 480
margin = 100

camera.resolution = (width,height)
camera.framerate = 24
image = np.empty((height,width,3), dtype=np.uint8)
camera.capture(image,'bgr')
#grabbed, frame = capture.read()
frame = cv2.rotate(image, cv2.ROTATE_180)

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


#circles = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)
bestCircle = (-1, (-1,-1))
for contour in contours:
    (x, y), radius = cv2.minEnclosingCircle(contour)
    center = (int(x), int(y))
    radius = int(radius)
    if(radius > bestCircle[0]):
        bestCircle = (radius, center)

ball_place = "none" if bestCircle[1][0] == -1 else "right" if bestCircle[1][0] > width/2+margin else "left" if bestCircle[1][0] < width/2-margin else "middle"
print(ball_place)

if bestCircle[1][0] != -1:
    cv2.circle(frame, bestCircle[1], bestCircle[0], (0, 255, 0), 2) # tennis ball outline
    cv2.circle(frame, bestCircle[1], 1, (0, 0, 255), 2)      # tennis ball centroid

#masked = cv2.bitwise_and(frame,frame, mask=mask)
#result = cv2.addWeighted(frame, 1, circles, 1, 0)

if cv2.waitKey(30) & 0xFF == 27:
    exit

cv2.imwrite("photo.png", frame)
##capture.release()
##cv2.destroyAllWindows()
