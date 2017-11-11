cd yolo-9000
cat yolo9000-weights/x* > yolo9000-weights/yolo9000.weights # it was generated from split -b 95m yolo9000.weights
md5 yolo9000-weights/yolo9000.weights # d74ee8d5909f3b7446e9b350b4dd0f44  yolo9000.weights
cd darknet 
make # Will run on CPU. For GPU support, scroll down!

