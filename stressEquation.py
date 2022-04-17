import cv2
import numpy as np

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
