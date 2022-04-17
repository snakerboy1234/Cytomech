import tkinter as tk #possibly nessesary unsure
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os
import re

SCALEDOWNFACTOR = 0.2 #This is a magic number but what can ya do. I dont have a good way of getting image resolution.
SCALEUPFACTOR = 2.0
GAIN = 13.2
DISTANCE_BETWEEN_TEETH = 10
PREDEFINED_LENGTH = 5.738
ONLYINCREASING = 0
USING_EXCEL_DATA_CHANGE = 1

#following sort function taken from stack overflow
#preforms a numerical sort on images luckily this will not be relevant for actual use of these functions.
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

PATH = r'C:\Users\osipo\Desktop\CaptureFilesSeperated\test2Files'

#f is designation within listdir that checks if the object is a function but this should read through the directory in the path above and give a list of strings that are the file names
imageFileNameList = [f for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH,f))]
voltageList = [1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.6,2.5,2.4,2.3,2.2,2.1,2,1.9,1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1,0.5,0.1]
imageList = np.empty(len(imageFileNameList), dtype=cv2.Mat)
imageFileNameListSorted = sorted(imageFileNameList, key=numericalSort)

i = 0
for i in range(0, len(imageFileNameListSorted)):
    imageList[i] = cv2.imread(os.path.join(PATH, imageFileNameListSorted[i]))
i = 0
#imageList = [0] This is a test function of images as if incorporated from the GUI code base

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

def hysteresis (strainArray, stressArray, switchPoint, TEST, BUG_TESTING_TEXT_OUTPUT_FILE):

    #const variable initialization
    SIZEOFGUASSDATATWENTYFOUR = 24

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

    integralExponential = 0
    integralLogarithmic = 0

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
    x  = np.linspace(0.0001, 1, 101)
    data = np.genfromtxt('GAUSS-24.dat',
                     skip_header=1,
                     skip_footer=1,
                     names=True,
                     dtype=None,
                     delimiter=' ')

    #maxValueIndexOfStressArray = np.argmax(strainArray) do not trust use of numpy as it is a different color. Maybe its better
    lengthOfStrainArray = len(strainArray)
    lengthOfStressArray = len(stressArray)#Bug checking value

    #bug checking value
    if(lengthOfStrainArray != lengthOfStressArray):
        print('mismatched strain and stress arrays inputed within hysteresis function')
        return 0
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
    
    print('past strain value check')
    sys.stdout.flush()

    #bug checkin value
    if(indexWithMaximumValueInStrainArray == -1):
        print('no value in strain array over -1')
        return 0
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

    print('past switch point check')
    sys.stdout.flush()

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

    print('past arraySplitCheck')
    sys.stdout.flush()

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

        yEst = np.polyfit(stressArrayDecreasing, strainArrayDecreasing, 16)
        #A = np.vstack([stressArrayDecreasing, np.ones(len(stressArrayDecreasing))]).T
        #beta, log_alpha = np.linalg.lstsq(A, np.log(strainArrayDecreasingAbs), rcond = None)[0]
        #alpha = np.exp(log_alpha)

        print('past exponential equation')
        sys.stdout.flush()

        #should obtain a increasing function of the form y=(C)ln(Dx)

        yEst2 = np.polyfit(stressArrayIncreasing, strainArrayIncreasing, 16)
        #C = np.vstack([stressArrayIncreasing, np.ones(len(stressArrayIncreasing))]).T
        #Delta, log_cappa = np.linalg.lstsq(C, np.log(strainArrayIncreasingAbs), rcond = None)[0]
        #Cappa = np.exp(log_cappa/Delta)

    else:
        i == i


    #linear model
    linearModel = np.polyfit(strainArrayArr,stressArrayArr,1)
    modLinearModel = np.poly1d(linearModel)

    slope = (modLinearModel(2)-modLinearModel(1))/1
    print(slope)

    #beta = 9999
    #Delta = -999999

    sys.stdout.flush()
    a = plt.figure(figsize = (10,8))
    axes= a.add_axes([0.1,0.1,0.8,0.8])
    #plt.plot(strainArrayIncreasingAbs, splitStressArrayIncreasing, 'b.')#ln
    #plt.plot(strainArrayDecreasingAbs, splitStressArrayDecreasing, 'b.')#e
    if(ONLYINCREASING == 0):

        axes.plot(stressArrayDecreasing, strainArrayDecreasing, 'o')
        #axes.plot(stressArrayDecreasing, np.polyval(yEst, stressArrayDecreasing))
        axes.plot(stressArrayIncreasing, strainArrayIncreasing, 'o')
        #axes.plot(stressArrayIncreasing, np.polyval(yEst, stressArrayIncreasing))

        #plt.plot(x, alpha*np.exp(beta*x), 'r')
        #plt.plot(x, (Cappa*np.log(np.absolute(Delta*x))+2), 'r')

    else:

        i == i

    A = np.vstack([strainArrayArr, np.ones(len(strainArrayArr))]).T

    stressArrayArr = stressArrayArr[:, np.newaxis]

    alpha = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),stressArrayArr)
    print(alpha)

    axes.plot(x, alpha[0]*x-.077, 'r')
    plt.xlim([0,0.5])
    plt.ylim([-0.2,0.2])
    plt.show()
    plt.xlabel('strain')
    plt.ylabel('stress (Pa)')
    plt.title('Hyteresis Curve')
    plt.show()
    plt.savefig('hystersis_curve.png')

    GLOuter = (leftbound - rightbound)/2
    GLInner = (leftbound + rightbound)/2

    if(ONLYINCREASING == 0):

        i = 0

        while(i < SIZEOFGUASSDATATWENTYFOUR):

            combineRootWeightValues = data[i]

            root = combineRootWeightValues[0]
            weight = combineRootWeightValues[1]

            integralExponential = (GLOuter) * (weight) *(alpha * np.exp(beta * (GLOuter) * root * (GLInner))) + integralExponential 

            i = i + 1


    return  0

def bwareaopen(img, min_size, connectivity=8):
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
            img, connectivity=connectivity)
        
        # check size of all connected components (area in pixels)
        for i in range(num_labels):
            label_size = stats[i, cv2.CC_STAT_AREA]
            
            # remove connected components smaller than min_size
            if label_size < min_size:
                img[labels == i] = 0
                
        return img

def ImageAnalysis(voltageList, imageList, Gain, distanceBetweenTeeth, predefiniedLength):

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
    lengthArray = []
    strainArray = []
    stressArray = []
    forceArray  = []
    stressArrayToPascals = []

    #these values exist but will be deleted in final code
    amplifiedVoltageArray = []
    electricFieldArray = []
    forceArray = []

    cropImageSidesListTest = [319, 156, 194, 154]

    BUG_TESTING_TEXT_OUTPUT_FILE = open("bugReport.txt", "w+")

    print("data sent through")

    while(i < numFrames):
        lengthArray.append(0)
        i = i + 1
    i = 0
    while(i < (len(voltageList))):
        strainArray.append(0)
        stressArray.append(0)
        amplifiedVoltageArray.append(0)
        electricFieldArray.append(0)
        forceArray.append(0)
        stressArrayToPascals.append(0)
        i = i + 1
    i = 0

    print("lists set up")

    PI = np.pi

    tempStressArray = np.empty(numFrames, dtype=object) 

    #needs to be changed to consider new data
    while ((i < numFrames) and (TEST != 1)):
 
        frame = imageList[i]
        frameScaled = cv2.resize(frame, None, fx= SCALEDOWNFACTOR, fy= SCALEDOWNFACTOR, interpolation= cv2.INTER_LINEAR)#daniels images are in 4k ULTRA resolution. Opencv HATES this so this will scale it down hopefully with little data loss
        frameNormalized = cv2.normalize(frameScaled, dst=None, alpha=0, beta=500, norm_type=cv2.NORM_MINMAX)#beta and alpha are magic numbers. I dont really understand why .tiff files are like this
        height, width, channels = frameNormalized.shape

        #will obtain a cropped image named pletelet
        grayPlatelet = cv2.cvtColor(frameScaled, cv2.COLOR_BGR2GRAY)

        thresholdValue, plateletImgThresholdApplied = cv2.threshold(grayPlatelet, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)#attepmt at otsus thresholding techniques.

        print("initial opencv finished")

        if(SKIP_MANUAL_IMAGE_CROP == 1):
            imCrop = plateletImgThresholdApplied[int(cropImageSidesListTest[1]):int(cropImageSidesListTest[1]+cropImageSidesListTest[3]), int(cropImageSidesListTest[0]):int(cropImageSidesListTest[0]+cropImageSidesListTest[2])]
            #imCrop = plateletImgThresholdApplied[156:310, 319:513]
            #non manual image crop for testing for specific test case
        elif(i == 0):
            # Select ROI
            fromCenter = False #Designates ROI not auto defined from center allowing user input in opencv function
            cropImageSidesList = cv2.selectROI("Crop Stage user input required", plateletImgThresholdApplied, fromCenter) #function for selection of region of interest

            # Crop image
            imCrop = plateletImgThresholdApplied[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])] #using obtained regions of interest crop is preformed

            # Display cropped image
            cv2.imshow("cropped image", imCrop)
            resizedCrop = cv2.resize(imCrop, None, fx= SCALEUPFACTOR, fy= SCALEUPFACTOR, interpolation= cv2.INTER_LINEAR)
            cv2.imshow("cropped image resized", resizedCrop)

        elif(i != 0):
            imCrop = plateletImgThresholdApplied[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])]
        else:
            BUG_TESTING_TEXT_OUTPUT_FILE.write("value of i is unexpected error")
            BUG_TESTING_TEXT_OUTPUT_FILE.close()
            sys.exit()


        whitePixelsOnScreen =  np.sum(imCrop == 255)
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

        #j = 0
        #k = 0
        #XLim = cropImageSidesList[3] - cropImageSidesList[1]
        #YLim = cropImageSidesList[2] - cropImageSidesList[0]

        #these values present data but are incorrect

        j = int(cropImageSidesList[1])
        k = int(cropImageSidesList[0])
        XLim = int(cropImageSidesList[3] + cropImageSidesList[1])
        YLim = int(cropImageSidesList[2] + cropImageSidesList[0])

        longestLengthOfImageArrayWhitePixels = 0

        #finding longest length of pixel in given image

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

            k = int(cropImageSidesList[0])
            pixelCheckGate = 0
            j = j + 1

            if(lengthOfImageArrayWhitePixels > longestLengthOfImageArrayWhitePixels):
                longestLengthOfImageArrayWhitePixels = lengthOfImageArrayWhitePixels
                lengthOfImageArrayWhitePixels = 0
            else:
                lengthOfImageArrayWhitePixels = 0

        print("longest length found")
        #defining pixel length and area with given pixel length with outside parameters with first run barring that some other value

        if((i == 0) or (lengthOfPixel == -1)):
            numberOfWhitePixels = np.sum(plateletBinarizedHoleFilterClearedBordersWSmallObjectsFilter == 255) 

            lengthOfPixel = predefiniedLength/longestLengthOfImageArrayWhitePixels

            #platelet area will not change but this is possibly a area of bug checking, large area change implies bad data or occlusion
            areaOfPlateletInitial = numberOfWhitePixels * lengthOfPixel

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

        lengthArray[i] = longestLengthOfImageArrayWhitePixels * lengthOfPixel

        #testing function will be deleted in final product

        if(TEST == 1):
            hysteresis()
        else:
            i = i + 1;
            #do nothing

    #while loop split
    i = 0
    while(i < (len(lengthArray) - 1)):

        j = i + 1

        if(lengthArray[i] == 0):
            print('radius array zero')
            #not nessesarily an error but will tell user that there is no value here
        elif(lengthArray[i] != 0):
            strainArray[i] = (lengthArray[j] - lengthArray[i])/lengthArray[i]
        else:
            print('length array error')
            exit()

        i = i + 1


    print("strain array discovered")
    i = 0
    while(i < (len(voltageList))):
        amplifiedVoltageArray[i] = voltageList[i]*Gain
        electricFieldArray[i] = amplifiedVoltageArray[i]/distanceBetweenTeeth
        i = i + 1

    electricFieldToForce(electricFieldArray, forceArray)

    i = 0
    while(i < len(stressArray)):
        stressArray[i] = forceArray[i]/areaOfPlateletInitial
        stressArrayToPascals[i] = stressArray[i] * pow(10,12)
        i = i + 1

    print("stress discovered")
    print("strain values")
    print(strainArray)
    print("stress values pascals")
    print(stressArrayToPascals)

    hysteresis(strainArray, stressArrayToPascals, 20, TEST, BUG_TESTING_TEXT_OUTPUT_FILE)

    # release the video capture object
    plateletVideoData.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()

ImageAnalysis(voltageList, imageList, GAIN, DISTANCE_BETWEEN_TEETH, PREDEFINED_LENGTH)



