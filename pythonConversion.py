import tkinter as tk #possibly nessesary unsure
import cv2
import numpy as np
import imclearborders
import bwareaopen
import stressEquation
import matplotlib.pyplot as plt
import time
import hysteresisCurve as hC
import sys

#test is on
TEST = 0
SKIP_MANUAL_IMAGE_CROP = 1
ALLOW_PRINTS_FOR_TESTING = 1

plateletVideoData = cv2.VideoCapture(r"C:\Users\osipo\Desktop\platelet.avi")
FPS = int(plateletVideoData.get(cv2.CAP_PROP_FPS))
width  = plateletVideoData.get(cv2.CAP_PROP_FRAME_WIDTH)
height = plateletVideoData.get(cv2.CAP_PROP_FRAME_HEIGHT)
#This is a function known to be glitchy
numFrames = int(plateletVideoData.get(cv2.CAP_PROP_FRAME_COUNT))
platelet = 0
i = 0
j = 0
k = 0
pixelCheckGate = 0
numberOfWhitePixels = 0
lengthOfImageArrayWhitePixels = 0
longestLengthOfImageArrayWhitePixels = -1

radiusArray = []
strainArray = []
stressArray = []
voltageArray = [12,24,36,24,12]

BUG_TESTING_TEXT_OUTPUT_FILE = open("bugReport.txt", "w+")

while(i < numFrames):
    radiusArray.append(0)
    i = i + 1
i = 0
while(i < (numFrames-1)):
    strainArray.append(0)
    stressArray.append(0)
    i = i + 1
i = 0

MINUMUMSIZEOFPXIELS = 7961/2 #value of a combined platelet halved should ensure only platelet sized objects appear.
PI = np.pi

tempStressArray = np.empty(numFrames, dtype=object) 

while ((plateletVideoData.isOpened()) and (TEST != 1)):
 
    # Capture frame-by-frame
    ret, frame = plateletVideoData.read()
    if ret == True:

        # Display the resulting frame
        #cv2.imshow('Frame',frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

  # Break the loop
    else: 
        break
    #will obtain a cropped image named pletelet
    grayPlatelet = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    thresholdValue, plateletImgThresholdApplied = cv2.threshold(grayPlatelet, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)#attepmt at otsus thresholding techniques.


    if(SKIP_MANUAL_IMAGE_CROP == 1):
        r = [319, 156, 194, 154]
        imCrop = plateletImgThresholdApplied[156:310, 319:513]
        #non manual image crop for testing
    elif(i == 0):
        # Select ROI
        fromCenter = False #Designates ROI not auto defined from center allowing user input in opencv function
        r = cv2.selectROI("Image", plateletImgThresholdApplied, fromCenter) #function for selection of region of interest

        # Crop image
        imCrop = plateletImgThresholdApplied[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])] #using obtained regions of interest crop is preformed

        print(int(r[1]), int(r[1]+r[3]), int(r[0]), int(r[0]+r[2])) #test function

        # Display cropped image
        cv2.imshow("Image", imCrop)
        #cv2.waitKey(0)
    elif(i != 0):
        imCrop = plateletImgThresholdApplied[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    else:
        BUG_TESTING_TEXT_OUTPUT_FILE.write("value of i is unexpected error")
        BUG_TESTING_TEXT_OUTPUT_FILE.close()
        sys.exit()

    #Filling platelet holes. 
    plateletFloodFilled = plateletImgThresholdApplied.copy()#preinitialization of platelet flood filled

    height, width = plateletImgThresholdApplied.shape[:2]#I am unable to understand what .shape() and cannot find what this is online but seems to give width and height with difference of n pixels

    mask = np.zeros((height+2, width+2), np.uint8)#creates a mask or a zeros array of same size and shape of given platelet matrix array. Values within this array are set to unsigned int lengths of 8

    cv2.floodFill(plateletFloodFilled, mask, (0,0), 255)#holes within the space selected are filled here

    plateletFloodFilledInverse = cv2.bitwise_not(plateletFloodFilled)
    plateletBinarizedHoleFilter = plateletImgThresholdApplied | plateletFloodFilledInverse
    plateletBinarizedHoleFilterClearedBorders = imclearborders.imclearborder(plateletBinarizedHoleFilter, 4)#put this definition into the function no nessecity for includes
    plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter = bwareaopen.bwareaopen(plateletBinarizedHoleFilterClearedBorders, MINUMUMSIZEOFPXIELS, 4)

    j = int(r[1])
    k = int(r[0])
    XLim = int(r[1]+r[3])
    YLim = int(r[0]+r[2])

    while(j < XLim):
        while(k < YLim):
            if(plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter[j, k] == 255):
                pixelCheckGate = 1
                lengthOfImageArrayWhitePixels = lengthOfImageArrayWhitePixels + 1
            else:
                if(pixelCheckGate == 0):
                    i = i
                else:
                    break
            k = k + 1

        k = 0
        pixelCheckGate = 0

        j = j + 1

        if(lengthOfImageArrayWhitePixels > longestLengthOfImageArrayWhitePixels):
            longestLengthOfImageArrayWhitePixels = lengthOfImageArrayWhitePixels
        else:
            i = i

    if(longestLengthOfImageArrayWhitePixels == -1):
        print('there is either a bug with the length check or there is no vision object within the given parameters')
    elif(longestLengthOfImageArrayWhitePixels > -1):
        print(longestLengthOfImageArrayWhitePixels)
        i = i
    else:
        print('value of longestLengthOfImageArrayWhitePixels is not positive and below thought to be possible values')

    numberOfWhitePixels = np.sum(plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter == 255)   

    #radiusArray[i] = np.sqrt((numberOfWhitePixels)/(PI))
    radiusArray[i] = longestLengthOfImageArrayWhitePixels

    if(TEST == 1):
        hC.hysteresis()
    else:
        i = i + 1;
        #do nothing

i = 0
while(i < (len(radiusArray) - 1)):

    j = i + 1

    if(radiusArray[i] == 0):
        print('radius array zero error')
        exit()
    elif(radiusArray[i] != 0):
        strainArray[i] = (radiusArray[j] - radiusArray[i])/radiusArray[i]
    else:
        print('radius array error radius array is an expected data type')
        exit()

    i = i + 1


#this is where a theoretical strain function will go. I overlooked it right now

stressEquation.stressEquation(voltageArray, stressArray)

hC.hysteresis(strainArray, stressArray, 2, TEST, BUG_TESTING_TEXT_OUTPUT_FILE)

# release the video capture object
plateletVideoData.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
