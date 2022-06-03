
import serial
import time
import tkinter
import tkinter.font as font
from datetime import datetime
from PIL import ImageTk, Image
import imageAnalysis
import sys
 
import pypylon.pylon as py
import matplotlib.pyplot as plt
import numpy as np
import cv2
 
# SOME PART OF CAMERA CODE CREATES AN INSTANCE OF TK THAT USES PACK. SO WE CANNOT USE GRID AND WE HAVE TO
# ASSIGN EACH COMPONENT TO THE MASTER=FRAME
 
# Note that the camera code will throw exception if camera is not connected.
 
CAMERA_CONNECTED = 0
ARDUINO_CONNECTED = 1
TEST_OFFLINE = 0
TEST_DIRECTORY = "testImgs/Captured "
TEST_PHOTO_IDX = 0
 
if CAMERA_CONNECTED:
    # Locate & Initialize camera
    cam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
    cam.Open()
 
    # Reset to factory Defaults
    cam.UserSetSelector = "Default"
    cam.UserSetLoad.Execute()
 
    # Set to blk/white photo
    cam.PixelFormat = "RGB8"
    cam.Gain = 24
 
    # Take one picture - need dif approach for looping imgs
    # res = cam.GrabOne(1000)
 
    # Get array form of picture
    # img = res.Array
 
    # Display our image
    # plt.imshow(img)
 
 
# Below is the code for handling images in the background
# We need this so that our GUI still responds while pictures are being taken automatically
# We need to decide how many pictures we want to take with each burst, and whether the user tells us when to take or whether they are collected automatically
# We should also display the images as they are taken (or at least one from each burst) so that the user has some sense of what's actually happening
# If we want to do all camera management through our GUI, we should have a way for the user to see what's happening without saving the pictures to save space
 
# We also need to decide WHEN we want to calculate deformation. If we calculate it automatically then we could do so as soon as the images are taken.
# If we rely on the user to outline the image, we need to make sure that we hold onto the voltage value associated with the image until that time.
 
class HysteresisImgWrapper():
    def __init__(self, imageArray, voltageLevel):
        self.img = imageArray
        self.voltage = voltageLevel
        self.deformation = 0
 
converter = py.ImageFormatConverter()
converter.OutputPixelFormat = py.PixelType_BGR8packed
converter.OutputBitAlignment = py.OutputBitAlignment_MsbAligned
imgs = []
calibrationImg = 0
pixlength = 4.5
def takePhoto():
    # Takes a single photo of the current view. Blocks for 1sec to ensure proper photo saving.
 
    print("Saving photo as timestamp to save_images folder (must be in same folder as this script)")
    curDT = datetime.now()
    date_time = curDT.strftime("%m-%d-%Y_%Hh%Mm%Ss")
 
    if CAMERA_CONNECTED:
        result = cam.GrabOne(1000)
        img = result.Array # This is the format we want to save
 
    if TEST_OFFLINE:
        img = cv2.imread(TEST_DIRECTORY + str(TEST_PHOTO_IDX))
    # Convert & Resize image for GUI display
    PIL_image = Image.fromarray(np.uint8(img)).convert('RGB')
    PIL_image = PIL_image.resize((700,600))
    tk_image = ImageTk.PhotoImage(master=frame,image=PIL_image)
    imgLbl.config(image=tk_image)
    imgLbl.image = tk_image
 
    # Add image to our list
    if deformFlag.get() == 1:
        ocr, volt = voltageMap(voltage.get())
        imgs.append(HysteresisImgWrapper(img,volt))
 
    # If we are calibrating, send this image to the calibration function
    if calibrationFlag.get() == 1:
        pixlength = imageAnalysis.calibration(img)
 
    # Convert image for automatic saving. Note that we can replace this with a "Save" button in future if we want
    image = converter.Convert(result)
    img = image.GetArray() # This is the format converted to BGR for writing with OpenCV
 
    cv2.imwrite(saveFolderName.get() + '/%s.png'%date_time,img)
 
    # Now we can do whatever we want with the photos. We can allocate space in the GUI for an image and plop whichever we want from the burst in there.
    # Have to keep in mind that this handler is destroyed after each burst. Could do a global handler. Either way have to make sure we save any info we need.
 
def takeCalibrationPhoto():
    calibrationFlag.set(1)
    takePhoto()
    calibrationTxt.set('Calibrated!')
    calibrationFlag.set(0)
 
def analyzeData():
    pics = []
    volts = []
    length = len(imgs)
    distBetweenTeeth = 10
    gain = 1
 
    for img in imgs:
        pics.append(img.img)
        volts.append(img.voltage)
 
    stiffness, hystVal, plot = imageAnalysis.ImageAnalysis(volts,pics,gain,distBetweenTeeth,pixlength,stepDownIdx.get())
 
    stiffnessVal.set('Stiffness: ' + str(stiffness))
    hysteresisVal.set('Hysteresis: ' + str(hystVal))
 
    # Convert & Resize plot for GUI display
    PIL_image = Image.fromarray(np.uint8(plot)).convert('RGB')
    PIL_image = PIL_image.resize((700,600))
    tk_image = ImageTk.PhotoImage(master=frame,image=PIL_image)
    hysteresisLbl.config(image=tk_image)
    hysteresisLbl.image = tk_image
 
OCR1Avals = range(319,1279)
def voltageMap(userVoltage):
    # BASED ON EXPERIMENTALLY OBTAINED DATA
    # Min duty cycle is 20% = 4.06Vpp -> OCR1A = 319
    # Turning point is 40% = 80.4Vpp -> OCR1A = 639
    # Max duty cycle is 80% = 136.3Vpp -> OCR1A = 1279
    # For duty cycle 20-40%, slope is 3.69Vpp/%
    # For duty cycle 40-80%, slope is 1.25Vpp/%
    # If user-specified voltage < 4.06Vpp, set to 0
    # If voltage <= 20Vpp, use base value 4.5 and slope 0.114Vpp/d.c.
    # If user-specified voltage <= 80.4Vpp, use 0.304Vpp/d.c. and base value 0
    # If user-specified voltage > 80.4Vpp, use 0.0781Vpp/d.c. and base value 80.4
 
    reallyEarlySlope = 0.114
    lwrBnd = 3.0 #4.5
    cutoff = 0
    earlySlope = 0.21 #0.114 higher slope means lower output because it believes each increment does more power
    midSlope = 0.304
    lateSlope = 0.0781
 
    if userVoltage < 4.06:
        expectedVoltage = 0
        dutyCycle = 0
    elif userVoltage <= 10:
        expectedVoltage =  lwrBnd+ round( (userVoltage-lwrBnd)/reallyEarlySlope ) * reallyEarlySlope
        print("Input voltage " + str(userVoltage) + " mapped to " + str(expectedVoltage))
        dutyCycle = OCR1Avals[ round( (userVoltage-lwrBnd)/reallyEarlySlope  ) ]
    elif userVoltage <= 20:
        expectedVoltage =  lwrBnd+ round( (userVoltage-lwrBnd)/earlySlope ) * earlySlope
        print("Input voltage " + str(userVoltage) + " mapped to " + str(expectedVoltage))
        dutyCycle = OCR1Avals[ round( (userVoltage-lwrBnd)/earlySlope ) ]
    elif userVoltage <= 80.4:
        expectedVoltage =  cutoff + round( (userVoltage-cutoff)/midSlope ) * midSlope
        print("Input voltage " + str(userVoltage) + " mapped to " + str(expectedVoltage))
        dutyCycle = OCR1Avals[ round( (userVoltage-cutoff)/midSlope ) ]
    elif userVoltage <= 130:
        expectedVoltage =  80.4 + round( (userVoltage-80.4)/lateSlope ) * lateSlope
        print("Input voltage " + str(userVoltage) + " mapped to " + str(expectedVoltage))
        dutyCycle = OCR1Avals[ round( 325 + (userVoltage-80.4)/lateSlope ) ]
    else: # exceeded nominal range, reset
        dutyCycle = 0
        expectedVoltage = 0
 
   
    return dutyCycle,expectedVoltage
 
def quit():
   # ser.write('0'.encode())
   # cam.Close()
    frame.destroy()
    sys.exit("Exiting")
 
def incVoltage():
    print("Increasing Voltage " + str(voltage.get()))
    voltage.set(voltage.get() + float(incrementAmt.get()))
    dutyCycle, expectedVoltage = voltageMap(voltage.get())
    voltage.set(expectedVoltage)
    voltageTxt.set("Current Vpp (est): " + f'{expectedVoltage:.2f}')
   
    if ARDUINO_CONNECTED:
        ser.write(str(dutyCycle).encode())
        print(str(dutyCycle))
        time.sleep(0.5)
 
def decVoltage():
    print("Decreasing Voltage")
    newVoltage = voltage.get() - float(incrementAmt.get())
    if newVoltage < 0:
        newVoltage = 0
    print("New voltage is " + str(newVoltage))
    voltage.set(newVoltage) # CHANGE THIS TO UPDATE BY SET VOLTAGE INCREMENT
    dutyCycle, expectedVoltage = voltageMap(voltage.get())
    voltage.set(expectedVoltage)
    voltageTxt.set("Current Vpp (est): " + f'{expectedVoltage:.2f}')
    if ARDUINO_CONNECTED:
        ser.write(str(dutyCycle).encode())
        print(str(dutyCycle))
        time.sleep(0.5)
 
def setTurningPoint():
    stepDownIdx.set(len(imgs))
    print("Turning point is " + str(stepDownIdx.get()))
 
def resetVoltage():
    voltage.set(0)
    increm.set('5.0')
    decVoltage()
 
if ARDUINO_CONNECTED:
    ser = serial.Serial('com3', 9600)
    ser.write('0'.encode())
 
frame = tkinter.Tk()
frame.geometry('1800x800')
frame.title("Cytomech DEP Controller")
 
lgFont = "Times 20 bold"
 
 
# Frames below are used as reference locations for quasi-grid format.
top = tkinter.Frame(frame)
bottom = tkinter.Frame(frame)
topleft = tkinter.Frame(top)
topright = tkinter.Frame(top)
bottomleft = tkinter.Frame(bottom)
bottomright = tkinter.Frame(bottom)
 
top.pack(side="top")
bottom.pack(side="bottom")
topleft.pack(side="left")
topright.pack(side="right")
bottomleft.pack(side="left")
bottomright.pack(side="right")
 
# Initialize space on GUI where latest camera photo will be displayed
PIL_image = np.ones((700,600))*150
tk_image =  ImageTk.PhotoImage(master=frame,image=Image.fromarray(PIL_image))
imgLbl = tkinter.Label(top,image=tk_image,width=700,height=600)
imgLbl.pack(side="right")
 
# Initialize space on GUI where hysteresis plot will be displayed
hysteresisImg =  ImageTk.PhotoImage(master=frame,image=Image.fromarray(PIL_image))
hysteresisLbl = tkinter.Label(topright,image=hysteresisImg,width=700,height=600)
hysteresisLbl.pack(side="top")
 
# Initialize Stiffness & Hysteresis Labels
hysteresisVal = tkinter.StringVar()
stiffnessVal = tkinter.StringVar()
hysteresisVal.set("Hysteresis: N/A")
stiffnessVal.set("Stiffness: N/A")
 
hysteresisValLbl = tkinter.Label(topright, textvariable=hysteresisVal, font=lgFont, width = 15, height = 2)
stiffnessValLbl = tkinter.Label(topright, textvariable=stiffnessVal, font=lgFont, width = 15, height = 2)
 
 
# Create calibration button so user can take an image of the teeth to calibrate pixels:microns ratio
calibrationBtn = tkinter.Button(topleft,
    text="Take Calibration Photo",
    font=lgFont,
    command=takeCalibrationPhoto,
    height = 2,
    fg = "black",
    bg = 'light green',
    width = 18,
    bd = 5,
    activebackground='white'
)
 
# Create label so user knows whether they have calibrated or not
calibrationTxt = tkinter.StringVar()
calibrationTxt.set('Not Yet Calibrated')
calibrationLbl = tkinter.Label(topleft, textvariable=calibrationTxt, font=lgFont, width = 20, height = 2)
calibrationFlag = tkinter.IntVar()
calibrationFlag.set(0)
 
 
# Place Increment Amount label and entry box so the user can set the increment amount
incrementLbl = tkinter.Label(topleft, text="Increment Amount", font=lgFont, width = 15, height = 2)
 
increm = tkinter.StringVar()
increm.set('5.0')
incrementAmt = tkinter.Entry(topleft,
    font=lgFont,
    width = 1,
    bd = 5,
    textvariable=increm,
    justify = "center"
)
 
# Place Increment Amount label and entry box so the user can set the increment amount
saveImgsLbl = tkinter.Label(topleft, text="Image Saving Folder", font=lgFont, width = 15, height = 2)
 
saveFolderName = tkinter.StringVar()
saveFolderName.set('save_images')
saveImgsBox = tkinter.Entry(topleft,
    font=lgFont,
    width = 1,
    bd = 5,
    textvariable=saveFolderName,
    justify = "center"
)
 
# Place button to decrement voltage
decVoltageBtn = tkinter.Button(bottomleft,
    text="-",
    font=lgFont,
    command=decVoltage,
    height = 2,
    fg = "black",
    bg = 'yellow',
    width = 3,
    bd = 5,
    activebackground='white'
)
 
# Place message variable that tells the user the current estimated voltage
voltageTxt = tkinter.StringVar(master=frame)
voltage = tkinter.DoubleVar(master=frame)
voltage.set(0)
voltageTxt.set("Current Vpp (est): 0")
voltLbl = tkinter.Label(bottomleft,textvariable=voltageTxt, width = 18,font=lgFont)
 
 
# Place increment button
incVoltageBtn = tkinter.Button(bottomleft,
    text="+",
    font=lgFont,
    command=incVoltage,
    height = 2,
    fg = "black",
    bg = 'green',
    width = 4,
    bd = 5,
    activebackground='white'
)
 
# Place reset button. This resets voltage to 0
# MOVING FORWARD MIGHT BE GOOD TO HAVE A BUTTON TO RESET VOLTAGE AND A BUTTON TO RESET SAVED IMAGES
resetBtn = tkinter.Button(bottomleft,
    text="Reset",
    font=lgFont,
    command=resetVoltage,
    height = 2,
    fg = "black",
    bg = 'light gray',
    width = 4,
    bd = 5,
    activebackground='white'
)
 
# Place button to indicate whether we are currently in step up or step down phase of deformation on left side
stepDownIdx = tkinter.IntVar()
stepDownIdx.set(0)
stepDownBtn = tkinter.Checkbutton(topleft,
    font=lgFont,
    text = "Stepping Down",
    command=setTurningPoint
)
 
# Place button to indicate whether we are currently in step up or step down phase of deformation on left side
deformFlag = tkinter.IntVar()
deformBtn = tkinter.Checkbutton(topleft,
    font=lgFont,
    text = "Deforming",
    variable=deformFlag
)
 
# Place button to take a photo, which is displayed in the image area
photoBtn = tkinter.Button(bottomleft,
    text="Take Photo",
    font=lgFont,
    command=takePhoto,
    height = 2,
    fg = "black",
    bg = '#FF7715',
    width = 10,
    bd = 5,
    activebackground='white'
)
 
# Place button to analyze image data that we have collected so far and output a hysteresis chart to the GUI
analyzeBtn = tkinter.Button(bottomleft,
    text="Analyze Data",
    font=lgFont,
    command=analyzeData,
    height = 2,
    fg = "black",
    bg = 'light blue',
    width = 10,
    bd = 5,
    activebackground='white'
)
 
# Place button to quit, which resets voltage to 0 before exiting
quitButton = tkinter.Button(bottomleft,
    text="QUIT",
    font=lgFont,
    command=quit,
    height = 2,
    fg = "black",
    width = 5,
    bg = 'red',
    bd = 5
)
 
saveImgsLbl.pack(side="top")
saveImgsBox.pack(expand=True,fill='both',side="top")
calibrationLbl.pack(pady=(30,0), side="top")
calibrationBtn.pack(side="top")
incrementLbl.pack(pady=(30,0), side="top")
incrementAmt.pack(expand=True,fill='both',side="top")
decVoltageBtn.pack(padx = 10, pady = 10, ipadx=10,ipady=10,expand=True,fill='both',side="left")
voltLbl.pack(pady = 10,expand=True,fill='both',side="left")
incVoltageBtn.pack(padx = 10, pady = 10,ipadx=10,ipady=10,expand=True,fill='both',side="left")
resetBtn.pack(padx = 10, pady = 10,ipadx=10,ipady=10,expand=True,fill='both',side="left")
stepDownBtn.pack(pady=(30,0), expand=True,fill='both',side="top")
deformBtn.pack(pady=(30,0), expand=True,fill='both',side="top")
photoBtn.pack(padx = 10, pady = 10, ipadx=10,ipady=10,expand=True,fill='both',side="left")
analyzeBtn.pack(padx = 10, pady = 10, ipadx=10,ipady=10,expand=True,fill='both',side="left")
quitButton.pack(padx = 10, pady = 10,ipadx=10,ipady=10,expand=True,fill='both',side="left")
hysteresisValLbl.pack(side="right")
stiffnessValLbl.pack(side="right")
 
tkinter.mainloop()