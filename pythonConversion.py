import tkinter as tk
import cv2
import numpy as np
import imclearborders

plateletVideoData = cv2.VideoCapture('0-10Vp1.avi')
FPS = int(plateletVideoData.get(cv2.CAP_PROP_FPS))
width  = plateletVideoData.get(cv2.CAP_PROP_FRAME_WIDTH)
height = plateletVideoData.get(cv2.CAP_PROP_FRAME_HEIGHT)
platelet = 0
#length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) not nessesary for python opencv

while (plateletVideoData.isOpened()):
 
    # Capture frame-by-frame
    ret, frame = plateletVideoData.read()
    #will obtain a cropped image named pletelet
    grayPlatelet = cv2.cvtColor(plateletImg, cv2.COLOR_BGR2GRAY)
    thresholdValue, plateletImgThresholdApplied = cv2.threshold(plateletImg, 0, 255, cv2.THRESH_BINARY+cv.THRESH_OTSU)#attepmt at otsus thresholding techniques.
    
    #Filling platelet holes. 
    plateletFloodFilled = plateletImgThresholdApplied.copy()
    height, width = plateletImgThresholdApplied.shape[:2]#I am unable to understand what .shape() and cannot find what this is onlone but seems to give width and height with difference of n pixels
    mask = np.zeros((height+2, width+2), np.uint8)#creates a mask or a zeros array of same size and shape of given platelet matrix array. Values within this array are set to unsigned int lengths of 8

    cv2.floodFill(plateletFloodFilled, mask, (0,0), 255)

    plateletFloodFilledInverse = cv2.bitwise_not(plateletFloodFilled)
    plateletBinarizedHoleFilter = plateletImgThresholdApplied | plateletFloodFilledInverse
    plateletBinarizedHoleFilterClearedBorders = imclearborders.imclearborder(plateletBinarizedHoleFilter, 4)#put this definition into the function no nessecity for includes







 
# release the video capture object
cap.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
