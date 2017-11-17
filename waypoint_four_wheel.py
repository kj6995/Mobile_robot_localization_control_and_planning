import cv2
import numpy as np
import random
import math
from math import *
import serial
from xbee import ZigBee
from xbee.helpers.dispatch import Dispatch
import time


#sends data to xbee address
def sendData(address, datatosend):
  	zb.send('tx', dest_addr_long = address, dest_addr = UNKNOWN, data = datatosend)

cap = cv2.VideoCapture(1)
while(1):
	
	newTarget = "Yes"

	_,frame = cap.read()
	#frame = cv2.imread('/media/kushagra/New Volume/BTP USV/test_image_4.png')
	frame = cv2.blur(frame,(3,3))
	#Convert to hsv
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
	
	#find range of red color
	thresh_red = cv2.inRange(hsv,np.array((160, 80, 80)), np.array((180, 255, 255)))
	thresh2_red = thresh_red.copy()

	#Find contours in the threshold image
	_,contours,hierarchy = cv2.findContours(thresh_red,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	#Finding contour with maximum area and store it as best_cnt
	max_area = 0
	best_cnt = 0
	for cnt in contours:
		area = cv2.contourArea(cnt)
		if area > max_area:
			max_area = area
			best_cnt = cnt
	
	#Finding centroids of best_cnt and draw a circle there
	M = cv2.moments(best_cnt)
	cx1,cy1 = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
	cv2.circle(frame,(cx1,cy1),10,(0,255,255),-1)

	#find range of Green color
	thresh_green = cv2.inRange(hsv,np.array((20, 80, 80)), np.array((60, 255, 255)))
	thresh2_green = thresh_green.copy()

	#Find contours in the threshold image
	_,contours,hierarchy = cv2.findContours(thresh_green,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	#Finding contour with maximum area and store it as best_cnt
	max_area = 0
	best_cnt = 0
	for cnt in contours:
		area = cv2.contourArea(cnt)
		if area > max_area:
			max_area = area
			best_cnt = cnt

	#Finding centroids of best_cnt and draw a circle there
	M = cv2.moments(best_cnt)
	cx2,cy2 = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
	cv2.circle(frame,(cx2,cy2),10,(0,0,255),-1)

	cxavg = (cx1+cx2)/2
	cyavg = (cy1+cy2)/2
	cv2.circle(frame, (cxavg, cyavg), 3, (0, 255, 255), -1)
	
	#find range of blue color
	thresh_blue = cv2.inRange(hsv,np.array((70, 80, 80)), np.array((140, 255, 255)))
	thresh2_blue = thresh_blue.copy()

	#Find contours in the threshold image
	_,contours,hierarchy = cv2.findContours(thresh_blue,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	
	#Drawing all contours and draw a rectangle there
	#cv2.drawContours(frame,contours,-1,(0,255,255),3)
	arr[len(contours)] = 0

	for i in range(len(contours)):
		x,y,w,h = cv2.boundingRect(contours[i])
		cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255), 2)
		arr.append((x+0.5*w, y+0.5*h))

	r = 33.7 # 4.8*7
	l = 37   # 4.8*7.7
	kp1 = 0.05
	kp2 = 1.0

	for target in arr:
		dx = target[1] - cxavg
		dy = target[2] - cyavg
		error_theta = int(math.floor(degrees(atan2(dy,dx))))
		dist = math.sqrt(dx*dx + dy*dy)
		
		while dist > 10:
			dx = target[1] - cxavg
			dy = target[2] - cyavg
			error_theta = int(math.floor(degrees(atan2(dy,dx))))
			dist = math.sqrt(dx*dx + dy*dy)
			v = kp1*dist
			omega = kp2*error_theta

			phi_1 = (v - omega*l)/r
			phi_2 = (v + omega*l)/r
			dataString = 'a,'+str(phi_1)+',b,'+ str(phi_2)

			PORT = '/dev/ttyUSB0'
			BAUD_RATE = 9600

			UNKNOWN = '\xff\xfe' 
			WHERE = '\x00\x13\xA2\x00\x40\xF7\x0A\x50'

			# Open serial port
			ser = serial.Serial(PORT, BAUD_RATE)

			zb = ZigBee(ser)

			#test data sending method
			try:
				sendData(WHERE, dataString)
			except KeyboardInterrupt:
				break
			# #zb.halt()
			# ser.close()

	if dist < 10:
		phi_1 = 0
		phi_2 = 0
	
	#cv2.line(frame,(cxavg,cyavg),(tX,tY),(0,0,0),2)
	
	cv2.imshow('frame',frame) #Color image
	#cv2.imwrite('/media/kushagra/New Volume/BTP USV/result_image_4.png',frame)
	if cv2.waitKey(10) & 0xFF == ord('q'):
			cap.release()
			cv2.destroyAllWindows()
			break