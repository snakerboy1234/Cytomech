import tkinter as tk
import cv2
import numpy as np
import imclearborders
import matplotlib.pyplot as plt
import time
import hysteresisCurve as hC

#test is on
TEST = 1

plateletVideoData = cv2.VideoCapture(r"C:\Users\osipo\Desktop\platelet.avi")
FPS = int(plateletVideoData.get(cv2.CAP_PROP_FPS))
width  = plateletVideoData.get(cv2.CAP_PROP_FRAME_WIDTH)
height = plateletVideoData.get(cv2.CAP_PROP_FRAME_HEIGHT)
platelet = 0
#length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) not nessesary for python opencv

strainArray = [0]
stressArray = [0]

while ((plateletVideoData.isOpened()) and (TEST != 1)):
 
    # Capture frame-by-frame
    ret, frame = plateletVideoData.read()
    if ret == True:

        # Display the resulting frame
        cv2.imshow('Frame',frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

  # Break the loop
    else: 
        break
    #will obtain a cropped image named pletelet
    grayPlatelet = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresholdValue, plateletImgThresholdApplied = cv2.threshold(grayPlatelet, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)#attepmt at otsus thresholding techniques.
    
    cv2.imshow('data test',plateletImgThresholdApplied)

    time.sleep(5);
    #Filling platelet holes. 
    plateletFloodFilled = plateletImgThresholdApplied.copy()
    height, width = plateletImgThresholdApplied.shape[:2]#I am unable to understand what .shape() and cannot find what this is onlone but seems to give width and height with difference of n pixels
    mask = np.zeros((height+2, width+2), np.uint8)#creates a mask or a zeros array of same size and shape of given platelet matrix array. Values within this array are set to unsigned int lengths of 8

    cv2.floodFill(plateletFloodFilled, mask, (0,0), 255)

    plateletFloodFilledInverse = cv2.bitwise_not(plateletFloodFilled)
    plateletBinarizedHoleFilter = plateletImgThresholdApplied | plateletFloodFilledInverse
    plateletBinarizedHoleFilterClearedBorders = imclearborders.imclearborder(plateletBinarizedHoleFilter, 4)#put this definition into the function no nessecity for includes
    #plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter = imclearborders.bwareaopen(plateletBinarizedHoleFilterClearedBorders, 50, 8)

    cv2.imshow('cleared borders',plateletBinarizedHoleFilterClearedBorders)

    numberOfWhitePixels = np.sum(plateletBinarizedHoleFilterClearedBorders == 255);
    numberOfBlackPixels = np.sum(plateletBinarizedHoleFilterClearedBorders == 0);

    totalPixels = numberOfWhitePixels + numberOfBlackPixels;
    
    if(TEST == 1):
        hC.hysteresis()
    else:
        i = i;
        #do nothing




# release the video capture object
plateletVideoData.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
