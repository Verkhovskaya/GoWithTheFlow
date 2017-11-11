import subprocess

cmd = "./darknet detector test cfg/combine9k.data cfg/yolo9000.cfg ../yolo9000-weights/yolo9000.weights "

def darknet(filename):
    result = subprocess.run((cmd + filename).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result

result = darknet("data/horses.jpg")
print(result.stdout)
print(result.stderr)
