import tkinter as tk #possibly nessesary unsure
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img
import time
import sys
import os
import re

SCALEDOWNFACTOR = 0.2 #This is a magic number but what can ya do. I dont have a good way of getting image resolution.
SCALEUPFACTOR = 2.0
GAIN = 1
DISTANCE_BETWEEN_TEETH = 10
PREDEFINED_LENGTH = 5.004
ONLYINCREASING = 0
USING_EXCEL_DATA_CHANGE = 1
TEST = 0
PATH = 1
SWITCH_POINT = 11
USING_SPONSER_VALUES = 0
MAX_INTENSITY_FROM_OPENCV = 32

FACTOR_FOUR = 4

VERBOSE = 1
VERYVERBOSE = 0

calibrationImage = cv2.imread("Captured.tif")

#following sort function taken from stack overflow
#preforms a numerical sort on images luckily this will not be relevant for actual use of these functions.
def setup():

    PATH = 1

    if(PATH == 1):
        numbers = re.compile(r'(\d+)')
        def numericalSort(value):
            parts = numbers.split(value)
            parts[1::2] = map(int, parts[1::2])
            return parts

        PATH = r'C:\Users\osipo\Desktop\06.02.22\T1.newpower'

        #f is designation within listdir that checks if the object is a function but this should read through the directory in the path above and give a list of strings that are the file names
        imageFileNameList = [f for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH,f))]
        voltageList = [15.18,20.06,24.93,29.79,34.66,39.52,44.38,49.52,54.11,58.98,63.84,58.98,54.11,49.52,44.38,39.52,34.66,29.79,24.93,20.01,14.97,9.95,4.94,0]
        strainValuesImportedList = [5.004,5.219,5.786,6.068,6.363,6.247,5.867,5.772,5.772,4.955]
        imageList = np.empty(len(imageFileNameList), dtype=cv2.Mat)
        imageFileNameListSorted = sorted(imageFileNameList, key=numericalSort)

        i = 0
        for i in range(0, len(imageFileNameListSorted)):
            imageList[i] = cv2.imread(os.path.join(PATH, imageFileNameListSorted[i]))
        i = 0

        return voltageList, imageList
#imageList = [0] This is a test function of images as if incorporated from the GUI code base

#removes image data from borders causing issues
#This function is cursed, Im serious here for some reason looking at the files it is spitting out causes it to think find contours is failing to recieve 3 outputs. There is no sane explaination for this.

def imclearborders(imgBW, radius):

    # Given a black and white image, first find all of its contours
    imgBWcopy = imgBW.copy()
    contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_SIMPLE)

    # Get dimensions of image
    imgRows = imgBW.shape[0]
    imgCols = imgBW.shape[1]    

    contourList = [] # ID list of contours that touch the border

    # For each contour...
    for idx in np.arange(len(contours)):
        # Get the i'th contour
        cnt = contours[idx]

        # Look at each point in the contour
        for pt in cnt:
            rowCnt = pt[0][1]
            colCnt = pt[0][0]

            # If this is within the radius of the border
            # this contour goes bye bye!
            check1 = (rowCnt >= 0 and rowCnt < radius) or (rowCnt >= imgRows-1-radius and rowCnt < imgRows)
            check2 = (colCnt >= 0 and colCnt < radius) or (colCnt >= imgCols-1-radius and colCnt < imgCols)

            if check1 or check2:
                contourList.append(idx)
                break

    for idx in contourList:
        cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

    return imgBWcopy

#Changes electrical feild measurements into force measurments using predefinied curve fitting outputs force array

def electricFieldToForce(voltageArray, stressArray):

    i = 0

    x = 0
    xPowerTwo = 0
    xPowerThree = 0
    xPowerFour = 0

    if(USING_EXCEL_DATA_CHANGE == 1):

        A = 6*(pow(10, -11))
        B = 6*(pow(10, -12))
        C = 9*(pow(10, -12))

        while(i < len(voltageArray)):

            x = voltageArray[i]
            xPowerTwo = pow(x, 2)

            stressArray[i] = (A*xPowerTwo)+(B*x)+C

            i = i + 1

    elif(USING_EXCEL_DATA_CHANGE != 1):
        A = 4.9*(pow(10, -14))
        B = 1.2*(pow(10, -12))
        C = 6.5*(pow(10, -11))
        D = -2.4*(pow(10, -11))

        while(i<len(voltageArray)):

            x = voltageArray[i]
            xPowerTwo = pow(x, 2)
            xPowerThree = pow(x, 3)
            xPowerFour = pow(x, 4)

            stressArray[i] = (A*xPowerFour)+(B*xPowerThree)+(C*xPowerTwo)+(D*x)

            i = i + 1

    else:
        i == i

    return 0

#Takes input of stress and strain arrays and test point to generate linear regression and polynomial curve fitting out puts hysteresis and graph data

def hysteresis (strainArray, stressArray, switchPoint, TEST, BUG_TESTING_TEXT_OUTPUT_FILE):

    #const variable initialization

    largestStress  = max(stressArray)
    smallestStress = min(stressArray)

    largestStrain  = max(strainArray)
    smallestStrain = min(strainArray)

    SIZEOFGUASSDATATWENTYFOUR = 21

    #initialization of iterators
    i = 0
    j = 0

    #intialize int variables
    indexWithMaximumValueInStrainArray = -1
    midpoint = 0
    leftbound = 0
    rightbound = 0

    GLOuter = 0
    GLInner = 0

    integral = 0
    
    valHysteresis = 0

    root = 0
    weight = 0

    #initialize double variables
    maxValueInStrainArray = 0.0

    #intialize list variables
    splitStrainArrayIncreasing = []
    splitStressArrayIncreasing = []
    splitStrainArrayDecreasing = []
    splitStressArrayDecreasing = []

    #test initialization 
    if(TEST == 1):

        strainArray = [0]
        stressArray = [0]
    
        x  = np.linspace(0.0001, 1, 101)
        y  = 0.1*np.exp(0.3*x) + 0.1*np.random.random(len(x))
        x2 = np.linspace(0, 10, 101)
        y2 = np.log(9*x) + 0.1*np.random.random(len(x))

    #end of test initialization
    x  = np.linspace(-2, 10, 10000)
    data = np.genfromtxt('GAUSS-24.dat',
                     skip_header=0,
                     skip_footer=0,
                     names=True,
                     dtype=None,
                     delimiter=' ')

    print(data)

    #maxValueIndexOfStressArray = np.argmax(strainArray) do not trust use of numpy as it is a different color. Maybe its better
    lengthOfStrainArray = len(strainArray)
    lengthOfStressArray = len(stressArray)#Bug checking value

    #bug checking value
    if(lengthOfStrainArray != lengthOfStressArray):
        print('mismatched strain and stress arrays inputed within hysteresis function')
        return 0, 0, 0
    else:
        #else do nothing
        i=i
    
    print('past bug checking')
    sys.stdout.flush()

    #while loop finds maximum value in the strain array
    #unchecked for off by one errors
    while(i < lengthOfStrainArray):

        if(maxValueInStrainArray < strainArray[i]):
            maxValueInStrainArray = strainArray[i]
            indexWithMaximumValueInStrainArray = i
        else:
            #else do nothing
            i=i

        i = i + 1
   

    #bug checkin value
    if(indexWithMaximumValueInStrainArray == -1):
        strainArray = np.abs(strainArray)
        largestStrain  = max(strainArray)
        smallestStrain = min(strainArray)
        #return 0
    else:
        #else do nothing
        i=i

    i = 0

    #Creates stress/strain array for increasing values
    #unchecked for off by one errors
    while(i <= switchPoint):

        splitStrainArrayIncreasing.append(strainArray[i])
        splitStressArrayIncreasing.append(stressArray[i])

        if(TEST == 1):
            #overwrite with testing
            splitStrainArrayIncreasing[i] = x
            splitStressArrayIncreasing[i] = y
        else:
            i=i
            #else do nothing

        i = i + 1

    #creates stress/strain array for decreasing values
    #unchecked for off by one errors

    while(i < lengthOfStrainArray):

        splitStrainArrayDecreasing.append(strainArray[i])
        splitStressArrayDecreasing.append(stressArray[i])

        if(TEST == 1):
            #overwrite with testing
            splitStrainArrayIncreasing[i] = x2
            splitStressArrayIncreasing[i] = y2
        else:
            i=i
            #else do nothing

        i = i + 1
        j = j + 1

    #should obtain a decreasing function of the form y=Ae^(Bx)

    i = 0
    j = 0

    stressArrayArr = np.asarray(stressArray)
    strainArrayArr = np.asarray(strainArray)

    stressArrayDecreasing = np.asarray(splitStressArrayDecreasing)
    strainArrayDecreasing = np.asarray(splitStrainArrayDecreasing)
    strainArrayDecreasingAbs = np.absolute(splitStrainArrayDecreasing)

    stressArrayIncreasing = np.asarray(splitStressArrayIncreasing)
    strainArrayIncreasing = np.asarray(splitStrainArrayIncreasing)
    strainArrayIncreasingAbs = np.absolute(splitStrainArrayIncreasing)

    if(ONLYINCREASING == 0):
        while(i<len(stressArrayIncreasing)):
            print(stressArrayIncreasing[i])

            i = i + 1


        i = 0
        while(i<len(stressArrayDecreasing)):

            print(stressArrayDecreasing[i])

            i = i + 1

        i = 0
        while(i < len(strainArrayIncreasing)):

            print(strainArrayIncreasing[i])

            i = i + 1

        i = 0
        while(i << len(strainArrayDecreasing)):

            print(strainArrayDecreasing[i])

            i = i + 1

        print('past exponential equation')
        sys.stdout.flush()

    else:
        i == i

    #beta = 9999
    #Delta = -999999

    stressArrayDecreasingArr = np.asarray(stressArrayDecreasing)
    stressArrayIncreasingArr = np.asarray(stressArrayIncreasing)
    strainArrayDecreasingArr = np.asarray(strainArrayDecreasing)
    strainArrayIncreasingArr = np.asarray(strainArrayIncreasing)

    strainArrayDecreasingSquared = np.square(strainArrayDecreasingArr)
    strainArrayIncreasingSquared = np.square(strainArrayIncreasingArr)

    print('strain decreasing')

    sys.stdout.flush()
    a = plt.figure(figsize = (10,8))
    axes= a.add_axes([0.1,0.1,0.8,0.8])
    #plt.plot(strainArrayIncreasingAbs, splitStressArrayIncreasing, 'b.')#ln
    #plt.plot(strainArrayDecreasingAbs, splitStressArrayDecreasing, 'b.')#e
    X = np.arange(0, 20)
    if(ONLYINCREASING == 0):
        axes.plot(strainArrayDecreasing, stressArrayDecreasing, 'o')
        #axes.plot(stressArrayDecreasing, np.polyval(yEst, X))
        axes.plot(strainArrayIncreasing, stressArrayIncreasing, 'o')
        #axes.plot(stressArrayIncreasing, np.polyval(yEst2, X))

        #plt.plot(x, alpha*np.exp(beta*x), 'r')
        #plt.plot(x, (Cappa*np.log(np.absolute(Delta*x))+2), 'r')

    else:

        i == i

    A = np.vstack([strainArrayArr, np.ones(len(strainArrayArr))]).T
    stressArrayArr = stressArrayArr[:, np.newaxis]

    linearSlope = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),stressArrayArr)

    print(linearSlope)

    B = np.vstack([strainArrayDecreasingArr, np.ones(len(strainArrayDecreasingArr))])
    B = np.vstack([strainArrayDecreasingSquared, B]).T

    stressArrayDecreasingArr = stressArrayDecreasingArr[:, np.newaxis]

    polyValuesDecreasing = np.dot((np.dot(np.linalg.inv(np.dot(B.T,B)),B.T)),stressArrayDecreasingArr)#error when non inversible matrix found

    print(polyValuesDecreasing)

    C = np.vstack([strainArrayIncreasingSquared, strainArrayIncreasingArr, np.ones(len(strainArrayIncreasingArr))]).T
    stressArrayIncreasingArr = stressArrayIncreasingArr[:, np.newaxis]

    polyValuesIncreasing = np.dot((np.dot(np.linalg.inv(np.dot(C.T,C)),C.T)),stressArrayIncreasingArr)#error when non inversible matrix found

    print(linearSlope)
    axes.plot(x, linearSlope[0]*x+linearSlope[1], 'r', color = "blue")
    axes.plot(x, (polyValuesDecreasing[0]*x*x)+polyValuesDecreasing[1]*x+polyValuesDecreasing[2], 'r')
    axes.plot(x, (polyValuesIncreasing[0]*x*x)+polyValuesIncreasing[1]*x+polyValuesIncreasing[2], 'r')
    plt.ylim([smallestStress,largestStress])
    plt.xlim([smallestStrain,largestStrain])
    plt.xlabel('strain')
    plt.ylabel('stress (Pa)')
    plt.title('Stiffness Curve')
    plt.show()
    plt.savefig('hystersis_curve.png')

    plotImg = img.imread('hystersis_curve.png')

    print("stiffness", linearSlope[0], file = BUG_TESTING_TEXT_OUTPUT_FILE)

    integralDecreasing = 0
    integralIncreasing = 0
    GLOuter = (smallestStrain - largestStrain)/2
    GLInner = (smallestStrain + largestStrain)/2

    stiffness = linearSlope[0]

    if(ONLYINCREASING == 0):

        i = 0

        while(i < SIZEOFGUASSDATATWENTYFOUR):

            combineRootWeightValues = data[i]

            print(data[i])

            root = combineRootWeightValues[0]
            weight = combineRootWeightValues[1]

            integralDecreasing = (GLOuter) * (weight) * ((((polyValuesDecreasing[0]*root*root)+polyValuesDecreasing[1]*root+polyValuesDecreasing[2]) * GLOuter) +  (GLInner)) + integralDecreasing
            integralIncreasing = (GLOuter) * (weight) * ((((polyValuesIncreasing[0]*root*root)+polyValuesIncreasing[1]*root+polyValuesIncreasing[2]) * GLOuter) +  (GLInner)) + integralIncreasing

            i = i + 1

            integral = abs(integralIncreasing - integralDecreasing)

    print("hysteresis value", integral, file = BUG_TESTING_TEXT_OUTPUT_FILE)

    return stiffness, integral, plotImg

#takes image and min size to delete smaller image artifacts, connectivity is currently broken returns modified image

def bwareaopen(img, min_size, connectivity):
        """Remove small objects from binary image (approximation of 
        bwareaopen in Matlab for 2D images).
    
        Args:
            img: a binary image (dtype=uint8) to remove small objects from
            min_size: minimum size (in pixels) for an object to remain in the image
            connectivity: Pixel connectivity; either 4 (connected via edges) or 8 (connected via edges and corners).
    
        Returns:
            the binary image with small objects removed
        """
    
        # Find all connected components (called here "labels")
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            img)
        
        print("finds connected components")

        # check size of all connected components (area in pixels)
        for i in range(num_labels):
            label_size = stats[i, cv2.CC_STAT_AREA]
            
            # remove connected components smaller than min_size
            if label_size < min_size:
                img[labels == i] = 0
                
        return img
      
def fillInBlanks(strainList):
    #I despise this function as it invariably looses data but its the only way to get around limitations with pixels and resolution
    i = 0
    j = 1
    k = -1

    lengthOfStrainList = len(strainList)
    nextInLineForStrainList = 0

    while(i < lengthOfStrainList):

        if(strainList[i] == 0 & (i != 0)):
            while(strainList[i] == 0):
                j = j + 1
                nextInLineForStrainList = strainList[j]
                if(nextInLineForStrainList == 0):
                    i = i
                    #repeat
                elif(nextInLineForStrainList != 0):
                    
                    if(strainList[j] == 0):

                        i == i

                    elif(strainList[j] != 0):

                        strainList[i] = i

                else:
                    exit()


        i = i + 1
        j = i + 2
        k = i

    return 0

   # main function which preforms image analysis takes image list, voltage data, distance between teeth, the switchpoint, 
   # and gain, gain used solely during testing with daniels code and for our purposes is 1


def ImageAnalysis(voltageList, imageList, Gain, distanceBetweenTeeth, predefiniedLength, switchPoint, pixelLength):

    #test is on at 1
    TEST = 0
    SKIP_MANUAL_IMAGE_CROP = 0
    ALLOW_PRINTS_FOR_TESTING = 1
    JUST_OVER_TWO_THIRDS_A_PLATELET = 0.65

    #iterators
    i = 0
    j = 0
    k = 0

    numFrames = len(imageList)

    #these all seem like old values
    pixelCheckGate = 0
    numberOfWhitePixels = 0
    lengthOfImageArrayWhitePixels = 0
    longestLengthOfImageArrayWhitePixels = -1
    lengthOfPixel = -1

    #need to change designation to list as array is a sperate numpy class applicable to lists in math and functions
    lengthList = []
    strainList = []
    stressArray = []
    forceArray  = []
    areaList   = []
    stressArrayToPascals = []

    #these values exist but will be deleted in final code
    amplifiedVoltageArray = []
    electricFieldArray = []
    forceArray = []

    cropImageSidesListTest = [319, 156, 194, 154]

    BUG_TESTING_TEXT_OUTPUT_FILE = open("bugReport.txt", "w+")
    HISTOGRAM_TEXT_FILE = open("histogramFile.txt", "w+")
    VERY_VERBOSE_TXT_FILE = open("VERYVERBOSE.txt", "w+")

    while(i < numFrames):
        lengthList.append(0)
        i = i + 1
    i = 0
    while(i < (len(voltageList))):
        strainList.append(0)
        stressArray.append(0)
        amplifiedVoltageArray.append(0)
        electricFieldArray.append(0)
        forceArray.append(0)
        stressArrayToPascals.append(0)
        areaList.append(0)
        i = i + 1
    i = 0

    PI = np.pi

    tempStressArray = np.empty(numFrames, dtype=object) 

    #needs to be changed to consider new data
    while ((i < numFrames) and (TEST != 1)):
 
        frame = imageList[i]
        frameScaled = cv2.resize(frame, None, fx= SCALEDOWNFACTOR, fy= SCALEDOWNFACTOR, interpolation= cv2.INTER_LINEAR)#daniels images are in 4k ULTRA resolution. Opencv HATES this so this will scale it down hopefully with little data loss
        frameNormalized = cv2.normalize(frameScaled, dst=None, alpha=0, beta=500, norm_type=cv2.NORM_MINMAX)#beta and alpha are magic numbers. I dont really understand why .tiff files are like this

        #frameScaled = frame

        height, width, channels = frameNormalized.shape

        if(SKIP_MANUAL_IMAGE_CROP == 1):
            imCrop = plateletImgThresholdApplied[int(cropImageSidesListTest[1]):int(cropImageSidesListTest[1]+cropImageSidesListTest[3]), int(cropImageSidesListTest[0]):int(cropImageSidesListTest[0]+cropImageSidesListTest[2])]
            #imCrop = plateletImgThresholdApplied[156:310, 319:513]
            #non manual image crop for testing for specific test case
        elif(i == 0):
            # Select ROI
            fromCenter = False #Designates ROI not auto defined from center allowing user input in opencv function
            cropImageSidesList = cv2.selectROI("Crop Stage user input required", frameNormalized, fromCenter) #function for selection of region of interest

            # Crop image
            imCrop = frameNormalized[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])] #using obtained regions of interest crop is preformed

            # Display cropped image
            cv2.imshow("cropped image", imCrop)
            resizedCrop = cv2.resize(imCrop, None, fx= SCALEUPFACTOR, fy= SCALEUPFACTOR, interpolation= cv2.INTER_LINEAR)
            cv2.imshow("cropped image resized", resizedCrop)

        elif(i != 0):
            imCrop = frameNormalized[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])]
        else:
            BUG_TESTING_TEXT_OUTPUT_FILE.write("value of i is unexpected error")
            BUG_TESTING_TEXT_OUTPUT_FILE.close()
            sys.exit()


        grayPlatelet = cv2.cvtColor(imCrop, cv2.COLOR_BGR2GRAY)

        cv2.imshow("Gray filter on platelet", grayPlatelet)

        #finding grey scaled image height and width
        heightGS, widthGS = grayPlatelet.shape[:2]

        convertImageToSortedList(grayPlatelet, widthGS, heightGS, VERY_VERBOSE_TXT_FILE)

        #need to make seperate threshold function as otsus threshold is too powerful here
        thresholdValue, plateletImgThresholdApplied = cv2.threshold(grayPlatelet, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)#attepmt at otsus thresholding techniques.
        unusedVar = modifiedOtsuThreshold(grayPlatelet, 0, HISTOGRAM_TEXT_FILE)
        cv2.imshow("image threshold applied", plateletImgThresholdApplied)
        whitePixelsOnScreen =  np.sum(plateletImgThresholdApplied == 255)
        MINUMUMSIZEOFPXIELS = whitePixelsOnScreen*(JUST_OVER_TWO_THIRDS_A_PLATELET)

        print("white pixels finished")

        #Filling platelet holes. 
        plateletFloodFilled = plateletImgThresholdApplied.copy()#preinitialization of platelet flood filled
        height, width = plateletFloodFilled.shape[:2]#I am unable to understand what .shape() and cannot find what this is online but seems to give width and height with difference of n pixels
        mask = np.zeros((height+2, width+2), np.uint8)#creates a mask or a zeros array of same size and shape of given platelet matrix array. Values within this array are set to unsigned int lengths of 8
        cv2.floodFill(plateletFloodFilled, mask, (0,0), 255)#holes within the space selected are filled here
        plateletFloodFilledInverse = cv2.bitwise_not(plateletFloodFilled)
        plateletBinarizedHoleFilter = plateletImgThresholdApplied | plateletFloodFilledInverse
        plateletBinarizedHoleFilterClearedBorders = imclearborders(plateletBinarizedHoleFilter, 4)#put this definition into the function no nessecity for includes
        plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter = bwareaopen(plateletBinarizedHoleFilterClearedBorders, MINUMUMSIZEOFPXIELS, 4)

        print("mask found")

        if(i == 0):
            cv2.imshow("post processing image", plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter)
            cv2.waitKey(0)
        else:
            i = i

        PATH = 'C:/Users/osipo/Desktop/processedImageLocation/image{' + str(i) + '}.png'

        cv2.imwrite(PATH, grayPlatelet)

        j = 0
        k = 0
        XLim = int(cropImageSidesList[3] + cropImageSidesList[1])
        YLim = int(cropImageSidesList[2] + cropImageSidesList[0])

        height, width = plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter.shape

        longestLengthOfImageArrayWhitePixels = 0

        #finding longest length of pixel in given image

        print(height, width)

        j = 0
        k = 0
        while(k < (height - 1)):

            while(j < (width - 1)):

                if(plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter[k, j] == 255):
                    pixelCheckGate = 1
                    lengthOfImageArrayWhitePixels = lengthOfImageArrayWhitePixels + 1
                else:
                    if(pixelCheckGate == 0):
                        i = i
                    else:
                        break
                j = j + 1

            #k = int(cropImageSidesList[0])
            j = 0
            pixelCheckGate = 0
            k = k + 1

            if(lengthOfImageArrayWhitePixels > longestLengthOfImageArrayWhitePixels):
                longestLengthOfImageArrayWhitePixels = lengthOfImageArrayWhitePixels
                lengthOfImageArrayWhitePixels = 0
            else:
                lengthOfImageArrayWhitePixels = 0

        print("longest length found")
        #defining pixel length and area with given pixel length with outside parameters with first run barring that some other value

        lengthOfPixel = pixelLength

        if((i == 0) or (lengthOfPixel == -1)):
            numberOfWhitePixels = np.sum(plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter == 255) 

            #platelet area will not change but this is possibly a area of bug checking, large area change implies bad data or occlusion
            areaList[i] = numberOfWhitePixels * lengthOfPixel
            
            if(USING_SPONSER_VALUES == 1):
                areaOfPlateletInitial = 19.6664

            if((i == 0) and (lengthOfPixel == -1)):
                print("initial loop did not find pixel length")

        elif(i != 0):
            i = i
        else:
            exit()

        print("pixel length definied")
        #pixel length bug check

        if(longestLengthOfImageArrayWhitePixels == -1):
            print('there is either a bug with the length check or there is no vision object within the given parameters')
        elif(longestLengthOfImageArrayWhitePixels > -1):
            #print(longestLengthOfImageArrayWhitePixels)
            i = i
        else:
            print('value of longestLengthOfImageArrayWhitePixels is not positive and below thought to be possible values')  

        lengthList[i] = longestLengthOfImageArrayWhitePixels * lengthOfPixel

        #testing function will be deleted in final product

        if(TEST == 1):
            hysteresis()
        else:
            i = i + 1;
            #do nothing

    #while loop split
    i = 0
    while(i < (len(lengthList) - 1)):

        j = i + 1

        if((lengthList[i] == 0) and (i != 0)):
            print('radius array zero')
            strainList[i] = (lengthList[i] - lengthList[0])/lengthList[0]
            #not nessesarily an error but will tell user that there is no value here
        elif(lengthList[i] != 0):
            strainList[i] = (lengthList[i] - lengthList[0])/lengthList[0]
        else:
            print('testing with nothing assuming tiny initial value to prevent divide by zero error')
            strainList[i] = 0.000001

        i = i + 1

    strainList[0] = 0
    i = 0

    if(USING_SPONSER_VALUES == 1):
        while(i < len(strainValuesImportedList)):

            strainList[i] = (strainValuesImportedList[i] - strainValuesImportedList[0])/strainValuesImportedList[0]

            i = i + 1

    strainList[0] = 0
    print("strain array discovered")
    i = 0
    while(i < (len(voltageList))):
        amplifiedVoltageArray[i] = voltageList[i]*Gain
        electricFieldArray[i] = amplifiedVoltageArray[i]/distanceBetweenTeeth
        i = i + 1

    electricFieldToForce(electricFieldArray, forceArray)

    if(USING_SPONSER_VALUES == 0):
        areaOfPlateletInitial = sum(areaList)/len(areaList)
        areaOfPlateletInitial = areaOfPlateletInitial * FACTOR_FOUR

    i = 0
    while(i < len(stressArray)):
        stressArray[i] = forceArray[i]/areaOfPlateletInitial
        stressArrayToPascals[i] = stressArray[i] * pow(10,12)
        i = i + 1

    i = 0

    imageProcessingDataOverview(voltageList, strainList, stressArrayToPascals, BUG_TESTING_TEXT_OUTPUT_FILE)

    stiffness, valHysteresis, plotImg = hysteresis(strainList, stressArrayToPascals, switchPoint, TEST, BUG_TESTING_TEXT_OUTPUT_FILE)

    # Closes all the windows currently opened.
    cv2.destroyAllWindows()
    BUG_TESTING_TEXT_OUTPUT_FILE.close()

    return stiffness, valHysteresis, plotImg

#takes in a calibrating image showing the teeth to find pixel to micron length. Will bring up a image of teeth 

def calibration(image):

    pixelLength = 0

    frame = image
    frameScaled = cv2.resize(frame, None, fx= SCALEDOWNFACTOR, fy= SCALEDOWNFACTOR, interpolation= cv2.INTER_LINEAR)
    frameNormalized = cv2.normalize(frameScaled, dst=None, alpha=0, beta=500, norm_type=cv2.NORM_MINMAX)
    height, width, channels = frameNormalized.shape

    fromCenter = False #Designates ROI not auto defined from center allowing user input in opencv function
    cropImageSidesList = cv2.selectROI("Crop Stage user input required", frameScaled, fromCenter) #function for selection of region of interest

    # Crop image
    numberOfPixelsBetweenTeeth = int(cropImageSidesList[1]+cropImageSidesList[3])

    pixelLength = DISTANCE_BETWEEN_TEETH/numberOfPixelsBetweenTeeth

    return pixelLength

#This simply prints out to a txt file the data presented

def imageProcessingDataOverview(processedVoltageList, processedStrainList, processedStressList, BUG_TESTING_TEXT_OUTPUT_FILE):

    i = 0

    print("voltage values", end = "\n", file = BUG_TESTING_TEXT_OUTPUT_FILE)
    while(i < len(processedVoltageList)):

        print(processedVoltageList[i], end = ", ", file = BUG_TESTING_TEXT_OUTPUT_FILE)
        i = i + 1

    quartiles = np.percentile(voltageList, [25,50,75])
    max = np.max(processedVoltageList)
    min = np.min(processedVoltageList)

    print("\n 5 Number Summary Min: ",min,",Q1: ",quartiles[0],",Median: ",quartiles[1],",Q3: ",quartiles[2],",Max: ",max, end = "", file = BUG_TESTING_TEXT_OUTPUT_FILE)

    print("\n\n strain values", end = "\n", file = BUG_TESTING_TEXT_OUTPUT_FILE)
    i = 0

    while(i < len(processedStrainList)):

        print(processedStrainList[i], end = ", ", file = BUG_TESTING_TEXT_OUTPUT_FILE)
        i = i + 1

    quartiles = np.percentile(processedStrainList, [25,50,75])
    max = np.max(processedStrainList)
    min = np.min(processedStrainList)

    print("\n 5 Number Summary Min: ",min,",Q1: ",quartiles[0],",Median: ",quartiles[1],",Q3: ",quartiles[2],",Max: ",max, end = "", file = BUG_TESTING_TEXT_OUTPUT_FILE)

    print("\n\n stress values", end = "\n", file = BUG_TESTING_TEXT_OUTPUT_FILE)
    i = 0

    while(i < len(processedStressList)):

        print(processedStressList[i], end = ", ", file = BUG_TESTING_TEXT_OUTPUT_FILE)
        i = i + 1

    quartiles = np.percentile(processedStressList, [25,50,75])
    max = np.max(processedStressList)
    min = np.min(processedStressList)

    print("\n 5 Number Summary Min: ",min,",Q1: ",quartiles[0],",Median: ",quartiles[1],",Q3: ",quartiles[2],",Max: ",max, end = "", file = BUG_TESTING_TEXT_OUTPUT_FILE)

    print(" ", end = "\n")

    return 0

#will get this working currently part of the cursed bug in clear borders
def storeImagesExternally(imageList, i):

    if(VERYSHOWY == 1):
        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/greyImageData/greyPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[0])

        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/thresholdImageData/greyThresholdedPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[1])

        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/maskImageData/maskPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[2])

        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/floodFilledImageData/floodFilledPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[3])

        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/holeFilterImageData/holeFilterPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[4])

        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/clearedBordersImageData/clearedBordersPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[5])

    if(VERYSHOWY == 1 or SHOWY == 1):
        PATH = 'C:/Users/osipo/Desktop/imageProcessingFileDirectory/processedImageData/processedPlatelet{' + str(i) + '}.png'
        cv2.imwrite(PATH, imageList[6])

#Otsu's thresholding technique can be used for cases where bimodality exists within the image histogram but this would need to be predetermined
def modifiedOtsuThreshold(image, normalizationRequired, HISTOGRAM_TEXT_FILE):

    thresholdValue = 0

    #total bins nessesary within histogram
    binsNum = MAX_INTENSITY_FROM_OPENCV

    # find frequency of pixels in range 0-255
    histr = cv2.calcHist([image],[0],None,[256],[0,256])

    print("a", file = HISTOGRAM_TEXT_FILE)
    print(image, file = HISTOGRAM_TEXT_FILE)

    HISTOGRAM_TEXT_FILE.flush()

    # show the plotting graph of an image
    plt.plot(histr)
    plt.show()

    return thresholdValue

#sorts an images intensity values numerically from least to greatest for use later
def convertImageToSortedList(image, width, length, VERY_VERBOSE_TXT_FILE):

    i = 0
    j = 0
    k = 0

    intensityList = []
    sortedIntensityList = []

    pixelAmount = length * width

    while(i < pixelAmount):

        intensityList.append(0)
        sortedIntensityList.append(0)

        i = i + 1

    i = 0

    while(i < width-1):

        while(j < length-1):

            intensityList[k] = image[j, i]
            print(image[i, j])

            j = j + 1
            k + k + 1

        i = i + 1

    #This has n complexity do not use large images
    sortedIntensityList = intensityList.sort()

    if(VERBOSE == 1):
        print(intensityList, file = VERY_VERBOSE_TXT_FILE)
        print(sortedIntensityList, file = VERY_VERBOSE_TXT_FILE)
        VERY_VERBOSE_TXT_FILE.flush()

    return sortedIntensityList



voltageList, imageList = setup()

pixelLength = calibration(calibrationImage)

ImageAnalysis(voltageList, imageList, GAIN, DISTANCE_BETWEEN_TEETH, PREDEFINED_LENGTH, SWITCH_POINT, pixelLength)


