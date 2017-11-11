cd yolo-9000
cat yolo9000-weights/x* > yolo9000-weights/yolo9000.weights
md5 yolo9000-weights/yolo9000.weights
cd darknet 
git reset --hard b61bcf544e8dbcbd2e978ca6a716fa96b37df767
make

