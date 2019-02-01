#!/usr/bin/python

import cv2
import numpy as np
import sys


def normalize_rect(rect):
    """
    Make rectangle a rotated tall rectangle, which means y-size > x-size
    and the angle indicates the "tilt": rotation of the longer axis from vertical
    (or equivalently shorter side from horizon)
    :param rect: OpenCV's rectangle object
    :return: OpenCV's rectangle object normalized as described
    """
    # rect[0] is the coordinates of the center of the rectangle
    # rect[1] is tuple of the sizes (x, y)
    # rect[2] is the tilt angle
    if rect[1][0] > rect[1][1]:
        # if x > y then we turn it 90 degrees
        # which means swap the sizes and turn cw or ccw depending on the previous value
        new_angle = rect[2] + 90.0 if rect[2] < 0.0 else -90.0
        return (
            rect[0],                    # same coordinates
            (rect[1][1], rect[1][0]),   # flipped sizes
            new_angle
        )
    else:
        return rect


if len(sys.argv) < 2:
    print "Usage: {} image-file.png".format(sys.argv[0])
    sys.exit("No file name is given")

# read the image directly from the file into the frame object
frame = cv2.imread(sys.argv[1])
# we want csv color space because it's better suited for color filtering
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# these are two arrays for lower and upper boundaries of the color range
# get these "magic" numbers by running the "color-filter" experiment
minHSV = np.array([67, 150, 113])
maxHSV = np.array([81, 255, 255])

# create a bitmap based on the threshold values
mask_hsv = cv2.inRange(hsv, minHSV, maxHSV)
# find contours of the areas in the bitmap
contours, hierarchy = cv2.findContours(mask_hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# find image moments for each contour
moments = ([cv2.moments(x) for x in contours])
# find Hu moments for each contour
hu_moments = ([cv2.HuMoments(x) for x in moments])
# dunno what to do with these moments yet, just print them out for now
for a_moment in hu_moments:
    print a_moment

# find bounding rectangles around the contours and normalize them
# using our custom normalize_rect function to estimate their tilt
rectangles = ([normalize_rect(cv2.minAreaRect(x)) for x in contours])

# draw things on the original image
for rect in rectangles:
    # let's make right leaning rectangles pink and the left - yellow
    color = (255, 0, 255) if rect[2] > 0 else (0, 255, 255)
    xrect = (rect[0], (rect[1][0]+12, rect[1][1]+12), rect[2])
    # convert each rectangle into boxes and then contours before drawing
    display = cv2.drawContours(frame, [np.int0(cv2.boxPoints(xrect))], -1, color, 3)

# show the result in a window
cv2.imshow('image', display)
# wait indefinitely for a key pressed
cv2.waitKey(0)
# Clean up and quit
cv2.destroyAllWindows()
