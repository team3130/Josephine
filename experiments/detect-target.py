#!/usr/bin/python

from __future__ import print_function
import cv2
import numpy as np
import sys


def normalize_rect(rect):
    """
    Make rectangle a rotated tall rectangle, which means y-size > x-size
    and the angle indicates the "tilt": rotation of the longer axis from vertical
    :param rect: OpenCV's rectangle object
    :return: OpenCV's rectangle object normalized as described
    rect[0] is the coordinates of the center of the rectangle
    rect[1] is tuple of the sizes (x, y)
    rect[2] is the tilt angle
    if width > height, in rect's internal means, then we turn it 90 degrees
    which means swap the sizes and turn cw or ccw depending on the previous value
    """
    if rect[1][0] > rect[1][1]:
        # incoming rect can be a tuple so if swapping reassign the whole thing
        rect = (
            rect[0],                   # same center coordinates
            (rect[1][1], rect[1][0]),  # swap height with width
            rect[2] + 90.0 if rect[2] < 0.0 else -90.0
        )
    return rect


def score_two(rect1, rect2):
    """
    Calculate a score for two rectangles based on their positions and orientation
    :param rect1: Assumed "left" target
    :param rect2: Assumed "right" target
    :return: score
    """
    score = 0.0
    avg_width = (rect1[1][0] + rect2[1][0])/2
    avg_x = (rect1[0][0] + rect2[0][0])/2
    vector = np.array([rect2[0][0] - rect1[0][0], rect2[0][1] - rect1[0][1]])
    length = np.sqrt(np.dot(vector, vector))
    tilt_l = (14.5 - rect1[2])/15
    tilt_r = (14.5 + rect2[2])/15
    if length > 0:
        aim = (avg_x - mid_point)/mid_point
        ratio = 0.2 - avg_width / length
        sine = vector[1] / length
        cosine = vector[0] / length
        score += sine * sine
        score += (1 - cosine)
        score += ratio * ratio
        score += aim * aim
        score += tilt_l * tilt_l
        score += tilt_r * tilt_r
    return score


if len(sys.argv) < 2:
    print("Usage: {} image-file.png".format(sys.argv[0]))
    sys.exit("No file name is given")

# read the image directly from the file into the frame object
frame = cv2.imread(sys.argv[1])

frame_area = frame.shape[0] * frame.shape[1]
mid_point = frame.shape[0] / 2
min_area = frame_area / 50 / 50
max_area = frame_area / 10 / 10
print(max_area, min_area)

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

indexes = []
rectangles = []

for i in range(0, len(contours)):
    # find image moments for each contour
    moments = cv2.moments(contours[i])
    area = moments['m00']
    print("Area: {}".format(area))
    if area < min_area or area > max_area:
        print("Out of range.")
        continue

    # find Hu moments for each contour
    hu_moments = cv2.HuMoments(moments)
    # dunno what to do with these moments yet, just print them out for now
    # print(hu_moments)

    # find bounding rectangles around the contours and normalize them
    # using our custom normalize_rect function to estimate their tilt
    rectangle = normalize_rect(cv2.minAreaRect(contours[i]))

    # if all tests passed then append the rectangle to the set
    indexes.append(i)
    rectangles.append(rectangle)

min_score = None
best_pair = None
for i in range(len(indexes)):
    for j in range(len(indexes)):
        if i != j:
            score = score_two(rectangles[i], rectangles[j])
            print("{i}-{j} {x1}-{x2}: {score}".format(
                i=i, j=j,
                x1=rectangles[i][0][0], x2=rectangles[j][0][0],
                score=score
            ))
            if min_score is None or score < min_score:
                min_score = score
                best_pair = (i, j)

xrect = (
    (
        (rectangles[best_pair[0]][0][0] + rectangles[best_pair[1]][0][0])/2,
        (rectangles[best_pair[0]][0][1] + rectangles[best_pair[1]][0][1])/2
    ),
    (
        2 * abs(rectangles[best_pair[1]][0][0] - rectangles[best_pair[0]][0][0]),
        rectangles[best_pair[0]][1][1] + rectangles[best_pair[1]][1][1]
    ),
    0
)
cv2.drawContours(frame, [np.int0(cv2.boxPoints(xrect))], -1, (255, 255, 0), 3)

# draw things on the original image
for i in range(len(indexes)):
    # let's make right leaning rectangles pink and the left - yellow
    color = (255, 0, 255) if rectangles[i][2] > 0 else (0, 255, 255)
    xrect = (
        rectangles[i][0],
        (rectangles[i][1][0]+12, rectangles[i][1][1]+12),
        rectangles[i][2])
    cv2.drawContours(frame, [np.int0(cv2.boxPoints(xrect))], -1, color, 3)

# show the result in a window
cv2.imshow('image', frame)
# wait indefinitely for a key pressed
cv2.waitKey(0)
# Clean up and quit
cv2.destroyAllWindows()
