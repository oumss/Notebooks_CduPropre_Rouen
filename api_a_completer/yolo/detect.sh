# For JetsonNano (Ubuntu 18.04.06 LTS, Jetpack4.6.1, Python3.6.9, tensorflow-2.7.0+nv22.1, torch-1.10.0a0+git36449ea)
#python3 detect.py --device 0 weights/yolov5s.pt --source data/images/horses.jpg
#python3 detect.py --device 0 --weights weights/yolov5s.pt --source 1 # v5.0 0.142s
#python3 detect.py --device 0 --weights weights/yolov5s.pt --source 1 # v6.0 0.132s
#python3 detect.py --device 0 --weights weights/yolov5s.pt --source 1 # v6.1 0.132s 
#python3 detect.py --device 0 --weights weights/yolov5n.pt --source 1 # v6.0 0.064s
python3 detect.py --device 0 --weights weights/yolov5n.pt --source 0  # v6.1 0.063s
#python3 detect.py --device 0 --weights weights/yolov5n.engine --source 0 # v6.1 0.051s
