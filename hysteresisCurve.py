
import numpy as np

#This function will find the equations that bound the hysteresis curve then return the area bounded by these two curves

#implication that stress and strain arrays are same length when using this function
def hysteresis (strainArray, stressArray):

    #initialization of variables
    i = 0
    indexWithMaximumValueInStrainArray = -1
    maxValueInStrainArray = 0.0
    splitStrainArrayIncreasing = [0]
    splitStrainArrayDecreasing = [0]

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
        print('no value in strain array over -1')
        return 0
    else:
        #else do nothing
        i=i

    i = 0

    #Creates stress/strain array for increasing values
    #unchecked for off by one errors
    while(i < maxValueIndexOfStressArray):

        splitStrainArrayIncreasing[i] = strainArray[i]

        i = i + 1

    #creates stress/strain array for decreasing values
    #unchecked for off by one errors
    while(i < lengthOfStrainArray):

        splitStrainArrayDecreasing = strainArray[i]

        i = i + 1

    return  