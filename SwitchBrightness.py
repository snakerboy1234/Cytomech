#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

LedPin1 = 11    # pin17 --- led
LedPin2 = 22    # pin25 --- led
BtnPin1 = 12    # pin18 --- button
BtnPin2 = 40    # pin21 --- button

Led_status1 = 1
Led_status2 = 1
count1 = 0
p = None

        
def setup():
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        GPIO.setup(LedPin1, GPIO.OUT)   # Set LedPin's mode is output
        GPIO.setup(LedPin2, GPIO.OUT)
        GPIO.setup(BtnPin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
        GPIO.setup(BtnPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
        GPIO.output(LedPin1, GPIO.HIGH) # Set LedPin high(+3.3V) to off led
        GPIO.output(LedPin2, GPIO.HIGH) # Set LedPin high(+3.3V) to off led


def swLed1(ev=None):
        global Led_status1,count1
        #Led_status1 = not Led_status1
        count1 = count1+1
        p = GPIO.PWM(LedPin1, 100)
        p.start(0)
        if count1 % 4 == 1:
                print('1')
                Led_status1=1
                
                p.ChangeDutyCycle(100)
                time.sleep(1)
                #GPIO.output(LedPin1, Led_status1)  # switch led status(on-->off; off-->on)
        elif count1 % 4 == 2:
                print('2')
                Led_status1=1
                #while count1 % 4 == 2:
                p.ChangeDutyCycle(75)
                time.sleep(1)
                #time.sleep(10)
                #GPIO.output(LedPin1, Led_status1)
        elif count1 % 4 == 3:
                print('3')
                Led_status1=1
                #while count1 % 4 == 3:
                p.ChangeDutyCycle(50)
                time.sleep(1)
                #time.sleep(10)
                #GPIO.output(LedPin1, Led_status1)
        elif count1 % 4 == 0:
                print('4')
                Led_status1=0
               # while count1 % 4 == 0:
                p.ChangeDutyCycle(0)
                time.sleep(1)
                #time.sleep(10)
        #GPIO.output(LedPin1, Led_status1)

def swLed2(ev=None):
        global Led_status2
        Led_status2 = not Led_status2
        GPIO.output(LedPin2, Led_status2)  # switch led status(on-->off; off-->on)
        if Led_status2 == 1:
                print('led2 on...')
        else:
                print('...led2 off')
        
def loop():
        GPIO.add_event_detect(BtnPin1, GPIO.FALLING, callback=swLed1, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
        GPIO.add_event_detect(BtnPin2, GPIO.FALLING, callback=swLed2, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
        while True:
                time.sleep(1)   # Don't do anything
                      

def destroy():
        GPIO.output(LedPin1, GPIO.HIGH)     # led off
        GPIO.output(LedPin2, GPIO.HIGH)     # led off
        GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
        setup()
        try:
                loop()
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
                destroy()
