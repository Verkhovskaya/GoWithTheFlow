import cv2
import sys
import numpy as np
import time

video = cv2.VideoCapture(sys.argv[1])
paths = open(sys.argv[2]).read().split("\n")
print paths
exists, frame_one = video.read()
h, w, c = frame_one.shape
overlay = np.zeros((h, w, 3), np.uint8)

lineThickness = 2


for line in paths:
	data = line.strip().replace(",", " ").replace("[", " ").replace("]", " ").split(" ")
	data = filter(lambda x: x != "", data)
	for i in range(len(data)/2-1):
		x1 = int(data[2*i])
		y1 = int(data[2*i+1])
		x2 = int(data[2*i+2])
		y2 = int(data[2*i+3])
		cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 0), lineThickness)

cv2.imshow("overlay", overlay)
cv2.waitKey(0)

count = 1
out = cv2.VideoWriter('outpy.avi', -1, 20, (w, h))

while True:
	exists, frame = video.read()
	if not exists:
		break
	print "writing frame " + str(count)
	for line in paths:
		data = line.strip().replace(",", " ").replace("[", " ").replace("]", " ").split(" ")
		data = filter(lambda x: x != "", data)
		for i in range(len(data) / 2 - 1):
			x1 = int(data[2 * i])
			y1 = int(data[2 * i + 1])
			x2 = int(data[2 * i + 2])
			y2 = int(data[2 * i + 3])
			cv2.line(frame, (x1, y1), (x2, y2), (0, (255*(2*i-len(data)/2))*2/len(data), 0), lineThickness)
	cv2.imshow("overlaid video", frame)
	out.write(frame)
	cv2.waitKey(1)
	count += 1
