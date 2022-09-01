#Luca Cordes Dream Display
#libs to get via pip install opencv-python and pyserial
import cv2
import numpy as np
import serial
import time
import re
import time
import math

cap=cv2.VideoCapture('Lostasya.mp4')#file in the same folder
totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(totalFrames,'frames are available \nloading frames into ram')
frames=[]#convert mp4 to seqence of frames
for n in range(int(totalFrames)):
	ret, frame=cap.read()
	frames.append(frame)#writes the frames into RAM might be 4gb of ram usage in our case

lmax=2500# max mm des sensors 4m im datenblatt bigger than this value than the image is original size
lmin=50#smaller than this value and the image is 1 pixel
scaleingmethod="lin"#"lin" für linear "power" für eine funktion mit konsantem exponenten und natürlch "log" für logarithmisch
frametimer=0#timer for optional delay needed for delayframe 
delayframe=0.01# delay between each frame in SEC
listlength=30 #number of values to build an average from
arduino = serial.Serial(port='COM9', baudrate=115200, timeout=0.1)#select the right com prot
mml=[0]*listlength#list of mm distances the average of the last listlength of frames gets build and is very percise

def run(myFrameNumber):
	myFrameNumber=(totalFrames-1)-myFrameNumber #flip the zoom mode
	if myFrameNumber >= 0:
		#set frame position
		print('drawing frame',int(myFrameNumber))
		cv2.namedWindow( "dream", cv2.WINDOW_NORMAL );
		cv2.setWindowProperty("dream",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN);
		cv2.imshow('dream', frames[int(myFrameNumber)])
		cv2.waitKey(1)

while 1:
	data=arduino.readline()
	result = re.sub('[^0-9]','', data.decode('utf-8'))
	if(result!=''): #get good data only
		mml.append(int(result)*0.1)#add the new value
		mml.pop(0)#remove the oldest one
		mm=sum(mml)/len(mml)#write it into mm
		if(frametimer+delayframe<time.perf_counter()):#in s both
			frametimer=time.perf_counter()
			if scaleingmethod == "lin":
				b=-((totalFrames-1)/(lmax-lmin)*lmin)
				f=(totalFrames-1)/(lmax-lmin)*mm+b
			elif scaleingmethod == "power":
				#to the power of
				e=2
				a=(totalFrames-1)/(pow((lmax-lmin),e))
				f=a*pow((mm-lmin),e)
			elif scaleingmethod == "log":
				f=math.pow(math.pow(totalFrames,1/(lmax-lmin)),mm-lmin)-1
			else:
				print("wrong choice")
			if mm>lmax:
				f=totalFrames-1#cap it
			if mm<lmin:
				f=0
			run(f)