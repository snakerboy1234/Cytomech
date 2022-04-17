
import numpy as np
import sys
import matplotlib.pyplot as plt

#This function will find the equations that bound the hysteresis curve then return the area bounded by these two curves

#implication that stress and strain arrays are same length when using this function

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

    data = np.genfromtxt('GAUSS-24.dat',dtype=None,delimiter=' ')

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

    print(alpha)
    print(beta)

    i = 0
    while(i < SIZEOFGUASSDATATWENTYFOUR):

        combineRootWeightValues = data[i]

        root = combineRootWeightValues[0]
        weight = combineRootWeightValues[1]

        #works but the size of exp(beta is so small that integral expoenent goes to zero)
        integralExponential = (GLOuter) * (weight) *(alpha * np.exp(beta * (GLOuter) * root * (GLInner))) + integralExponential 

        i = i + 1

    return  0