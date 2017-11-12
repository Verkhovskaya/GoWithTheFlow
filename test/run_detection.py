
import os
import sys
import time
print time.time()

import random
import numpy as np
from sklearn.cluster import KMeans
import cv2

def move_to_edge(frame, position):
	up = frame[1]-position[1]
	down = position[1]
	right = frame[0] - position[0]
	left = position[0]
	distances = [up, right, down, left]
	go_to = distances.index(min(distances))
        widen = 0.1
        if go_to == 0:  # up
		return (max(0, position[0]-frame[0]*widen), frame[0]), (min(frame[0], position[0]+frame[0]*widen), frame[0])
	elif go_to == 1:  # right
		return (frame[0], max(0, position[1]-frame[1]*widen)), (frame[0], min(frame[1], position[1]+frame[1]*widen))
	elif go_to == 2:  # down
		return (max(0, position[0]-frame[0]*widen), 0), (min(frame[0], position[0]+frame[0]*widen), 0)
	elif go_to == 3:  # left
		return (0, max(0, position[1]-frame[1]*widen)), (0, min(frame[1], position[1]+frame[1]*widen))

class DataPoint:
	def __init__(self, tag, location, frame_id):
		self.tag = tag
		self.location = location
		self.frame_id = frame_id

	def __str__(self):
		return self.tag + " " + str(self.location) + " " + str(self.frame_id)

def unsupervised(data):
    max_k = 4
    iters = 1000
    n = 1
    k = [0] * max_k
    centers = []
    y_kmean = []
    
    X = np.array(data)
    #print(X)
    
    for i in range(max_k):
        kmeans = KMeans(n_clusters=(i+1))
        kmeans.fit(X)
        y_kmean.append(kmeans.predict(X))
        centers.append(np.array(kmeans.cluster_centers_, dtype=int))
        k[i] = kmeans.inertia_

    min_err = 99999999999999999
    min_err_index = 0
    for i in range(max_k):
        if (k[i] * (i+1) ** n) < min_err:
            min_err_index = i
            min_err = k[i]

    return (centers[min_err_index], y_kmean[min_err_index])

def run_detection(name):
    os.system("cp " + name + " ../yolo-9000/darknet/video.mp4")    
    os.chdir(os.path.dirname("../yolo-9000/darknet/script"))
    os.system("./../../test/script.sh")
    os.system("rm -rf video.mp4")
    os.system("mv output_00000100.jpg ..")
    os.system("rm -rf outp*")
    os.system("mv ../output_00000100.jpg .")
    os.system("mv output_00000100.jpg test_img.jpg")
    (centers, ends, y_vals), (s_centers, starts, sy_vals), paths = perform_localization()
    shape = draw_path(paths)
    os.chdir(os.path.dirname("../../test/run_detection.py"))

    #center is the center of the cluster
    #paths is the paths of each object
    #ends is the location of each end of each path
    #y_vals predicts which center the end corresponds to
    #s_centers contains the centers for the starting points
    #sy_vals predicts which starting point each point came from

    exits = []
    entrances = []
    for end in centers:
        exits.append(move_to_edge(shape, end))

    for enter in s_centers:
        entrances.append(move_to_edge(shape, enter))

    buckets = [0] * len(centers)
    s_buckets = [0] * len(s_centers)

    for i in range(len(y_vals)):
        buckets[y_vals[i]] += 1

    for i in range(len(sy_vals)):
        s_buckets[sy_vals[i]] += 1

    info = ((centers, ends, y_vals), (s_centers, starts, sy_vals), paths,\
    (exits, buckets), (entrances, s_buckets))

    #exits contains the range for each exit

def reset_openings(shape, ends, starts, openings):
    exits = openings["exits"]
    entrances = openings["entrances"]

    data_exits = []
    data_entrances = []
    for exit in exits:
        data_exits.append((exit[0] + exit[2])/2,(exit[1], exit[3])/2)

    for entrance in entrances:
        data_exits.append((entrance[0] + entrance[2])/2,(entrance[1], entrance[3])/2)

    exit_kmeans = KMeans(n_clusters=(len(exits)))
    entrance_kmeans = KMeans(n_clusters=(len(entrances)))

    exit_kmeans.cluster_centers_ = np.array(data_exits, dtype=int)
    entrance_kmeans.cluster_centers_ = np.array(data_entrances, dtype=int)

    y_vals = exit_kmeans.predict(ends)
    sy_vals = entrance_kmeans.predict(starts)

    buckets = [0] * len(exits)
    s_buckets = [0] * len(entrances)

    for i in range(len(y_vals)):
        buckets[y_vals[i]] += 1

    for i in range(len(sy_vals)):
        s_buckets[sy_vals[i]] += 1

    return buckets, s_buckets


def lin_distance(point1, point2):
	return abs(point1.location[0] - point2.location[0]) + abs(point1.location[1] - point2.location[1])

def find_closest(tracking, new_point):
	if not tracking:
		return None
	new_closest = tracking[0]
	for each in tracking[1:]:
		if lin_distance(each, new_point) < lin_distance(new_closest, new_point):
			new_closest = each
	return new_closest

def perform_localization():
    f = open("file.txt", "r")

    incoming = []
    for each in f:
    	new_frame = []
    	data = each.strip().replace(",", " ").replace("[", " ").replace("]", " ").split(" ")
    	data = filter(lambda x: x != "", data)
    	paired_data = []
    	for i in range(len(data)/2):
    		paired_data.append(['object', [int(data[2*i]), int(data[2*i+1])]])
    	incoming.append(paired_data)

    max_distance = 200
    max_frames_lost = 10

    by_tag = {}
    for frame in range(len(incoming)):
    	for each in incoming[frame]:
    		tag = each[0]
    		location = each[1]
    		if tag not in by_tag.keys():
    			by_tag[tag] = {}
    		if frame not in by_tag[tag].keys():
    			by_tag[tag][frame] = []
    		by_tag[tag][frame].append(DataPoint(tag, location, frame))

    links = []

    for tag in by_tag:
    	tag_data = by_tag[tag]
    	looking_for = []
    	for frame in tag_data:
    		for each in looking_for:
    			if frame - each.frame_id > max_frames_lost+1:
    				looking_for.remove(each)
    		this_frame_points = tag_data[frame]
    		new_tracked = []
    		while looking_for and this_frame_points:  # Find closest pair for each point last seen
    			closest_pairs = []
    			for point in looking_for:
    				closest_pairs.append((point, find_closest(this_frame_points, point)))
    			distances = map(lambda x: lin_distance(x[0], x[1]), closest_pairs)
    			closest_pair = closest_pairs[distances.index(min(distances))]  # Finds the closest pair
    			if lin_distance(closest_pair[0], closest_pair[1]) < max_distance:
    				links.append(closest_pair)
    				new_tracked.append(closest_pair[1])
    				this_frame_points.remove(closest_pair[1])
    				looking_for.remove(closest_pair[0])
    			else:
    				break
    		looking_for = new_tracked + this_frame_points  # + frame points adds new, previously untracked locations

    paths = []
    for each in links:
    	for i in range(len(paths)):
    		if paths[i][-1] == each[0]:
    			id_diff = each[1].frame_id - paths[i][-1].frame_id
    			if id_diff != 1:
    				for k in range(1,id_diff):
    					tag = each[0].tag
    					loc_0 = each[0].location[0] + k/id_diff*(each[1].location[0] - each[0].location[0])
    					loc_1 = each[0].location[1] + k/id_diff*(each[1].location[1] - each[0].location[1])
    					frame_id = each[0].frame_id + k
    					paths[i].append(DataPoint(tag, [loc_0, loc_1], frame_id))
    			paths[i].append(each[1])
    			break
    	else:
    		paths.append([each[0], each[1]])

    ends = []
    starts = []
    #print(paths)
    for each in paths:
        ends.append(each[-1].location)
        starts.append(each[0].location)

    os.system("rm -rf file.txt")
    centers, y_vals = unsupervised(ends)
    s_centers, sy_vals = unsupervised(starts)
    paths = [map(lambda x: x.location, each) for each in paths]
    print time.time()

    return (centers, ends, y_vals), (s_centers, starts, sy_vals), paths

def draw_path(paths):
    frame = cv2.imread("test_img.jpg")
    size = frame.shape
    lineThickness = 2
    scale  = 4
    print(paths)
    for line in paths:
    	data = filter(lambda x: x != "", line)
    	for i in range(len(data)-1):
    		x1 = int(data[i][0]*scale)
    		y1 = int(data[i][1]*scale)
    		x2 = int(data[i+1][0]*scale)
    		y2 = int(data[i+1][1]*scale)
    		cv2.line(frame, (x1, y1), (x2, y2), (150*(2*i-len(data)/2))*2/len(data), 0,150 - (150*(2*i-len(data)/2))*2/len(data), lineThickness)

    cv2.imwrite("lined_img.png", frame)
    return size
