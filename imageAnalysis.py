import tkinter as tk #possibly nessesary unsure
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

PATH = r'C:\Users\osipo\Desktop\CaptureFilesSeperated\test1Files'

#f is designation within listdir that checks if the object is a function but this should read through the directory in the path above and give a list of strings that are the file names
imageFileNameList = [f for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH,f))]
voltageList = [12,24,36,24,12]
imageList = numpy.empty(len(imageFileNameList), dtype=object)

print('file names able to be read')

for i in range(0, len(imageFileNameList)):
    imageList[i] = cv2.imread(join(PATH, imageFileNameList[i]))

#imageList = [0] This is a test function of images as if incorporated from the GUI code base

def imclearborder(imgBW, radius):

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

def stressEquation(voltageArray, stressArray):

    i = 0

    x = 0
    xPowerTwo = 0
    xPowerThree = 0
    xPowerFour = 0

    A = 4.9*(pow(10, -14))
    B = 1.2*(pow(10, -12))
    C = 6.5*(pow(10, -11))
    D = -2.4*(pow(10, -11))



    while(i<len(voltageArray)):

        x = voltageArray[i]
        xPowerTwo = pow(x,2)
        xPowerThree = pow(x, 3)
        xPowerFour = pow(x, 4)

        stressArray[i] = (A*xPowerFour)+(B*xPowerThree)+(C*xPowerTwo)+(D*x)

        i = i + 1

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

    #initialize numpy array variables
    x = np.linspace(0.0000000001, 0.00000015, 101)

    #test initialization 
    if(TEST == 1):

        strainArray = [0]
        stressArray = [0]
    
        x  = np.linspace(0.0001, 1, 101)
        y  = 0.1*np.exp(0.3*x) + 0.1*np.random.random(len(x))
        x2 = np.linspace(0, 10, 101)
        y2 = np.log(9*x) + 0.1*np.random.random(len(x))

    #end of test initialization

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

    while(i<len(stressArrayDecreasing)):

        print(stressArrayDecreasing[i])

        i = i + 1

    A = np.vstack([stressArrayDecreasing, np.ones(len(stressArrayDecreasing))]).T
    beta, log_alpha = np.linalg.lstsq(A, np.log(strainArrayDecreasingAbs), rcond = None)[0]
    alpha = np.exp(log_alpha)

    print('past exponential equation')
    sys.stdout.flush()

    #should obtain a increasing function of the form y=(C)ln(Dx)

    C = np.vstack([stressArrayIncreasing, np.ones(len(stressArrayIncreasing))]).T
    Delta, log_cappa = np.linalg.lstsq(C, np.log(strainArrayIncreasingAbs), rcond = None)[0]
    Cappa = np.exp(log_cappa/Delta)

    #linear model
    linearModel = np.polyfit(strainArrayArr,stressArrayArr,1)
    modLinearModel = np.poly1d(linearModel)

    print(beta)

    #beta = 9999
    #Delta = -999999

    sys.stdout.flush()

    plt.figure(figsize = (10,8))
    #plt.plot(strainArrayIncreasingAbs, splitStressArrayIncreasing, 'b.')#ln
    #plt.plot(strainArrayDecreasingAbs, splitStressArrayDecreasing, 'b.')#e
    plt.plot(x, alpha*np.exp(beta*x), 'r')
    plt.plot(x, (Cappa*np.log(np.absolute(Delta*x))+2), 'r')
    plt.plot(x, modLinearModel(x), color="green")
    plt.xlabel('strain')
    plt.ylabel('stress (Pa)')
    plt.title('Hyteresis Curve')
    plt.show()
    plt.savefig('hystersis_curve.png')

    GLOuter = (leftbound - rightbound)/2
    GLInner = (leftbound + rightbound)/2

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

def ImageAnalysis(voltageList, imageList):

    #test is on at 1
    TEST = 0
    SKIP_MANUAL_IMAGE_CROP = 1
    ALLOW_PRINTS_FOR_TESTING = 1

    #iterators
    i = 0
    j = 0
    k = 0

    #opencv variable designation
    plateletVideoData = cv2.VideoCapture(r"C:\Users\osipo\Desktop\platelet.avi")
    FPS = int(plateletVideoData.get(cv2.CAP_PROP_FPS))
    width  = plateletVideoData.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = plateletVideoData.get(cv2.CAP_PROP_FRAME_HEIGHT)
    #This is a function known to be glitchy
    numFrames = int(plateletVideoData.get(cv2.CAP_PROP_FRAME_COUNT))
    #platelet = 0

    #these all seem like old values
    pixelCheckGate = 0
    numberOfWhitePixels = 0
    lengthOfImageArrayWhitePixels = 0
    longestLengthOfImageArrayWhitePixels = -1

    #need to change designation to list as array is a sperate numpy class applicable to lists in math and functions
    radiusArray = []
    strainArray = []
    stressArray = []
    #voltageArray = [12,24,36,24,12]
    cropImageSidesListTest = [319, 156, 194, 154]

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
            imCrop = plateletImgThresholdApplied[int(cropImageSidesListTest[1]):int(cropImageSidesListTest[1]+cropImageSidesListTest[3]), int(cropImageSidesListTest[0]):int(cropImageSidesListTest[0]+cropImageSidesListTest[2])]
            #imCrop = plateletImgThresholdApplied[156:310, 319:513]
            #non manual image crop for testing for specific test case
        elif(i == 0):
            # Select ROI
            fromCenter = False #Designates ROI not auto defined from center allowing user input in opencv function
            cropImageSidesList = cv2.selectROI("Image", plateletImgThresholdApplied, fromCenter) #function for selection of region of interest

            # Crop image
            imCrop = plateletImgThresholdApplied[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])] #using obtained regions of interest crop is preformed

            print(int(cropImageSidesList[1]), int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]), int(cropImageSidesList[0]+cropImageSidesList[2])) #test function

            # Display cropped image
            cv2.imshow("Image", imCrop)
            #cv2.waitKey(0)
        elif(i != 0):
            imCrop = plateletImgThresholdApplied[int(cropImageSidesList[1]):int(cropImageSidesList[1]+cropImageSidesList[3]), int(cropImageSidesList[0]):int(cropImageSidesList[0]+cropImageSidesList[2])]
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

        j = 0
        k = 0
        XLim = cropImageSidesList[3] - cropImageSidesList[1]
        YLim = cropImageSidesList[2] - cropImageSidesList[0]

        #these values present data but are incorrect
        #j = int(cropImageSidesList[1])
        #k = int(cropImageSidesList[0])
        #XLim = int(cropImageSidesList[1]+cropImageSidesList[3])
        #YLim = int(cropImageSidesList[0]+cropImageSidesList[2])

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
            hysteresis()
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


    stressEquation(voltageList, stressArray)

    hysteresis(strainArray, stressArray, 2, TEST, BUG_TESTING_TEXT_OUTPUT_FILE)

    # release the video capture object
    plateletVideoData.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()

ImageAnalysis(voltageList, imageList)



