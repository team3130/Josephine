#!/usr/bin/python

import cv2
import numpy as np
import sys

if len(sys.argv) < 2:
    print "Usage: {} image-file.png".format(sys.argv[0])
    sys.exit("No file name is given")

# Read the image directly from the file into the frame object
frame = cv2.imread(sys.argv[1])
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# These are two arrays for lower and upper boundaries of the color range
minHSV = np.array([0, 0, 0])
maxHSV = np.array([255, 255, 255])


def update_boundaries(x=None):
    """
    This is the main processing code. Every time a slider on a trackbar moves
    this procedure is called as the callback
    """
    # get current positions of four trackbars
    maxHSV[0] = cv2.getTrackbarPos('Hmax', 'image')
    maxHSV[1] = cv2.getTrackbarPos('Smax', 'image')
    maxHSV[2] = cv2.getTrackbarPos('Vmax', 'image')
    minHSV[0] = cv2.getTrackbarPos('Hmin', 'image')
    minHSV[1] = cv2.getTrackbarPos('Smin', 'image')
    minHSV[2] = cv2.getTrackbarPos('Vmin', 'image')
    # create a bitmap based on the new threshold values
    mask_hsv = cv2.inRange(hsv, minHSV, maxHSV)
    # apply the bitmap mask on the original image
    display = cv2.bitwise_and(frame, frame, mask=mask_hsv)
    cv2.imshow('image', display)
    return x    # unneeded line, just to avoid warnings about unused x


# Create the output window with trackbars and assign the update function as callback
cv2.namedWindow('image')
# create trackbars for color change
cv2.createTrackbar('Hmax', 'image', 255, 255, update_boundaries)
cv2.createTrackbar('Hmin', 'image',   0, 255, update_boundaries)
cv2.createTrackbar('Smax', 'image', 255, 255, update_boundaries)
cv2.createTrackbar('Smin', 'image',   0, 255, update_boundaries)
cv2.createTrackbar('Vmax', 'image', 255, 255, update_boundaries)
cv2.createTrackbar('Vmin', 'image',   0, 255, update_boundaries)

# Update everything once to show the image the first time
update_boundaries()
# Wait indefinitely for a key pressed
cv2.waitKey(0)
# Clean up and quit
cv2.destroyAllWindows()
