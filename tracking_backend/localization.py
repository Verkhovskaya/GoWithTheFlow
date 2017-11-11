import sys
import time
print time.time()
args = sys.argv

f = open(args[1], "r")

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

"""
incoming = [
	[['person', [1, 1]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [2, 10]]],
	[['person', [1, 1]], ['dog', [1, 10]]],
	[['person', [1, 3]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [5, 5]], ['person', [1, 2]]],
	[['person', [1, 1]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [2, 10]]],
	[['person', [1, 1]], ['dog', [1, 10]]],
	[['person', [1, 3]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 2]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [2, 10]]],
	[['person', [1, 1]], ['dog', [1, 10]]],
	[['person', [1, 3]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 2]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 1]], ['dog', [2, 10]]],
	[['person', [1, 1]], ['dog', [1, 10]]],
	[['person', [1, 3]], ['dog', [1, 10]], ['person', [5, 5]]],
	[['person', [1, 2]], ['person', [5, 5]]]
	]
"""


class DataPoint:
	def __init__(self, tag, location, frame_id):
		self.tag = tag
		self.location = location
		self.frame_id = frame_id

	def __str__(self):
		return self.tag + " " + str(self.location) + " " + str(self.frame_id)


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

path_file = open('path_file.txt', 'w')
ends_file = open('ends_file.txt', 'w')

for each in paths:
	path_file.write(", ".join(map(lambda x: str(x.location), each)))
	path_file.write("\n")
	ends_file.write(str(each[-1].location[0]) + " " + str(each[-1].location[1]) + "\n")
print time.time()
