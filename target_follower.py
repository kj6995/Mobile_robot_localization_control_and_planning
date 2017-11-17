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
	
	_,frame = cap.read()
	#frame = cv2.imread('/media/kushagra/New Volume/BTP USV/test_image_4.png')
	#frame = cv2.blur(frame,(3,3))
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
	hx = cx1-cx2
	hy = cy1-cy2
	phi = int(math.floor(degrees(atan2(hy,hx))))
	print ("phi :%d" ,phi )
	
	#find range of blue color
	thresh_blue = cv2.inRange(hsv,np.array((70, 80, 80)), np.array((140, 255, 255)))
	thresh2_blue = thresh_blue.copy()

	#Find contours in the threshold image
	_,contours,hierarchy = cv2.findContours(thresh_blue,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

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
	tX,tY = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
	cv2.circle(frame,(tX,tY),10,(0,0,0),5)

	dx = tX - cxavg
	dy = tY - cyavg

	#Quad I -- Good
	if tX >= cxavg and tY <= cyavg:
		rads = atan2(dy,dx)
		degs = degrees(rads)
		degs = degs
		print "quad 4"
	#Quad II -- Good
	elif tX >= cxavg and tY >= cyavg:
		rads = atan2(dy,dx)
		degs = degrees(rads)
		print "quad 1"
	#Quad III
	elif tX <= cxavg and tY >= cyavg:
		rads = atan2(dy,dx)
		degs = degrees(rads)
		print"quad 2"
		#degs = 3
	elif tX <= cxavg and tY <= cyavg:
		rads = atan2(dy,dx)
		degs = degrees(rads)
		print "quad 3"
	
	targetDegs = int(math.floor(degs))
	print targetDegs

	error_theta = targetDegs - phi
	if error_theta < -180:
		error_theta += 360
	elif error_theta > 180:
		error_theta -= 360

	print("error_theta :",error_theta)
	dataString=''
	dist = math.sqrt(dx*dx + dy*dy)
	if dist < 10:
		dataString = '0/n'
		print dataString
	else:
		if -20 <= error_theta <= 20:
			dataString = '1/n'
			print dataString

		elif error_theta > 20:
			dataString = '3/n'
			print dataString

		elif error_theta < -20:
			dataString = '2/n'
			print dataString

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
	cv2.line(frame,(cxavg,cyavg),(tX,tY),(0,0,0),2)
	cv2.imshow('frame',frame) #Color image
	#cv2.imwrite('/media/kushagra/New Volume/BTP USV/result_image_4.png',frame)
	if cv2.waitKey(10) & 0xFF == ord('q'):
			cap.release()
			cv2.destroyAllWindows()
			break