#!/usr/bin/env python2

import time
import numpy as np
import cv2
import sys

n_frames = 60
timers = {"grab": 0, "convert": 0, "inrange": 0, "mask": 0}
image = np.empty((240 * 320 * 3,), dtype=np.uint8)

iam_on_pi = True
try:
    import picamera
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
except ImportError:
    iam_on_pi = False
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FPS, 15)

if not camera.isOpened():
    sys.exit("Cannot open a camera.")


def grab_frame(np_array):
    if iam_on_pi:
        camera.capture(np_array, 'bgr')
        return np_array.nonzero(), np_array.reshape((240, 320, 3))
    else:
        ret, np_array = camera.read(np_array)
        if ret:
            np_array = cv2.resize(np_array, (320, 200))
        return ret, np_array


ret, image = grab_frame(image)
if ret:
    cv2.imshow("Test window", image)
    print "Camera initialized. Sleeping for 2 seconds..."
    cv2.waitKey(2000)
else:
    sys.exit("Cannot capture an image")

if iam_on_pi:
    print "I am on PI"
else:
    print "Camera FPS: {}".format(camera.get(cv2.CAP_PROP_FPS))
    print "Camera WIDTH:  {}".format(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    print "Camera HEIGHT: {}".format(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

print "Starting camera capture..."
ret, image = grab_frame(image)
cv2.imshow("Test window", image)
cv2.waitKey(1000)

start_t = time.clock()
for i in range(n_frames):
    frame_t = time.clock()
    ret, image = grab_frame(image)
    if ret:
        timers["grab"] += time.clock() - frame_t
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        timers["convert"] += time.clock() - frame_t
        # create a bitmap based on the new threshold values
        mask_hsv = cv2.inRange(hsv, np.array([50, 80, 0]), np.array([90, 255, 255]))
        timers["inrange"] += time.clock() - frame_t
        # apply the bitmap mask on the original image
        display = cv2.bitwise_and(image, image, mask=mask_hsv)
        timers["mask"] += time.clock() - frame_t

    else:
        sys.exit("Couldn't grab a frame at iteration $i")
finish_t = time.clock()
print "Camera capture is done."

cv2.imshow("Test window", display)

print "Time elapsed:   {}".format(finish_t - start_t)
print "Effective FPS:  {}".format(n_frames/(finish_t - start_t))
print "Avg. capture:   {}".format(timers['grab']/n_frames)
print "Avg. convert:   {}".format((timers['convert'])/n_frames)
print "Avg. in range:  {}".format(timers['inrange']/n_frames)
print "Avg. mask:      {}".format(timers['mask']/n_frames)
print "Avg. iteration: {}".format((finish_t - start_t)/n_frames)

cv2.waitKey(0)
camera.release()
