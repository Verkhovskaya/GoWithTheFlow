#!/bin/bash

./darknet detector demo cfg/combine9k.data cfg/yolo9000.cfg ../yolo9000-weights/yolo9000.weights  -prefix output video.mp4  -thresh 0.15
