import serial
import time
import tkinter
import tkinter.font as font
from datetime import datetime
from PIL import ImageTk, Image
import sys

import pypylon.pylon as py
import matplotlib.pyplot as plt
import numpy as np
import cv2

# SOME PART OF CAMERA CODE CREATES AN INSTANCE OF TK THAT USES PACK. SO WE CANNOT USE GRID AND WE HAVE TO
# ASSIGN EACH COMPONENT TO THE MASTER=FRAME

# Note that the camera code will throw exception if camera is not connected.

# Locate & Initialize camera
cam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
cam.Open()

# Reset to factory Defaults
cam.UserSetSelector = "Default"
cam.UserSetLoad.Execute()

# Set to blk/white photo
cam.PixelFormat = "RGB8" 

# Take one picture - need dif approach for looping imgs
res = cam.GrabOne(1000)

# Get array form of picture
img = res.Array

# Display our image
plt.imshow(img)

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
def takePhoto():
    # Takes a single photo of the current view. Blocks for 1sec to ensure proper photo saving.

    print("Saving photo as timestamp to save_images folder (must be in same folder as this script)")
    curDT = datetime.now()
    date_time = curDT.strftime("%m-%d-%Y_%Hh%Mm%Ss")

    result = cam.GrabOne(1000)
    img = result.Array # This is the format we want to save

    # Convert & Resize image for GUI display
    PIL_image = Image.fromarray(np.uint8(img)).convert('RGB')
    PIL_image = PIL_image.resize((900,600))
    tk_image = ImageTk.PhotoImage(master=frame,image=PIL_image)
    imgLbl.config(image=tk_image)
    imgLbl.image = tk_image

    # Add image to our list
    voltage = voltageMap(voltIndex.get())
    imgs.append(HysteresisImgWrapper(img,voltage))

    # Convert image for automatic saving. Note that we can replace this with a "Save" button in future if we want
    image = converter.Convert(result)
    img = image.GetArray() # This is the format converted to BGR for writing with OpenCV

    cv2.imwrite('save_images/%s.png'%date_time,img)


    # Now we can do whatever we want with the photos. We can allocate space in the GUI for an image and plop whichever we want from the burst in there.
    # Have to keep in mind that this handler is destroyed after each burst. Could do a global handler. Either way have to make sure we save any info we need.
    

def voltageMap(voltageIndex):
    # Since the voltage scaling is sometimes nonlinear, this function will use a constant table of
    # practically attainable voltage values to determine what practical voltage is attained by the next increment
    # Note that, on the arduino side, the correspond to increments between OCR1A = 38 (25% d.c.) and OCR1A = 144 (90% d.c.)
    # We will not have an accurate table until we verify the whole electrical system in hardware

    voltMappings = [0,12,15,18,20,22,24,26,29] + [round(i*0.95) for i in range(31,107)]

    if voltageIndex < 0:
        return 0
    if voltageIndex > 84:
        return voltMappings[84]
    
    return voltMappings[voltageIndex]

def quit():
    ser.write(bytes([0]))
    cam.Close()
    frame.destroy()
    sys.exit("Exiting")

def incVoltage():
    if voltIndex.get() < 84:
        print("Increasing Voltage" + str(voltIndex.get()))
        voltIndex.set(voltIndex.get() + 1)
        voltageTxt.set("Current Vpp (est): " + str(voltageMap(voltIndex.get())))
        ser.write(bytes([voltIndex.get()]))

def decVoltage():
    if voltIndex.get() > 0:
        voltIndex.set(voltIndex.get() - 1)
        voltageTxt.set("Current Vpp (est): " + str(voltageMap(voltIndex.get())))
        print("Decreasing Voltage")
        if voltIndex.get() == 0:
            ser.write(bytes([0]))
        else:
            ser.write(bytes([voltIndex.get()]))

ser = serial.Serial('com3', 9600)
ser.write(bytes([0]))

frame = tkinter.Tk()
frame.geometry('1000x800')
frame.title("Cytomech DEP Controller")

lgFont = "Times 20 bold"

PIL_image = np.ones((900,600))*150
tk_image =  ImageTk.PhotoImage(master=frame,image=Image.fromarray(PIL_image))
imgLbl = tkinter.Label(frame,image=tk_image,width=900,height=600)
imgLbl.pack()

decVoltageBtn = tkinter.Button(frame,
    text="-",
    font=lgFont,
    command=decVoltage,
    height = 2,
    fg = "black",
    bg = 'yellow',
    width = 4,
    bd = 5,
    activebackground='white'
)
#decVoltageBtn.grid(row=1,column=1,rowspan=2, padx=20, pady=5)
decVoltageBtn.pack(padx = 10, pady = 10, ipadx=10,ipady=10,expand=True,fill='both',side="left")


voltageTxt = tkinter.StringVar(master=frame)
voltIndex = tkinter.IntVar(master=frame)
voltIndex.set(0)
voltageTxt.set("Current Vpp (est): 0")
voltLbl = tkinter.Label(frame,textvariable=voltageTxt, width = 15,font=lgFont)
#voltLbl.grid(row=3,column=1,columnspan=3, padx=20, pady=5)
voltLbl.pack(pady = 10,expand=True,fill='both',side="left")

incVoltageBtn = tkinter.Button(frame,
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
#incVoltageBtn.grid(row=1,column=3,rowspan=2)
incVoltageBtn.pack(padx = 10, pady = 10,ipadx=10,ipady=10,expand=True,fill='both',side="left")

photoBtn = tkinter.Button(frame,
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
#photoBtn.grid(row=4,column=1,rowspan=2, padx=20, pady=5)
photoBtn.pack(padx = 10, pady = 10, ipadx=10,ipady=10,expand=True,fill='both',side="left")

quitButton = tkinter.Button(
    frame,
    text="QUIT",
    font=lgFont,
    command=quit,
    height = 2,
    fg = "black",
    width = 5,
    bg = 'red',
    bd = 5
)
#quitButton.grid(row=4,column=3,rowspan=2, padx=20, pady=5)
quitButton.pack(padx = 10, pady = 10,ipadx=10,ipady=10,expand=True,fill='both',side="left")

tkinter.mainloop()