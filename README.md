# Face Detection and Tracking System

This system combines face detection using OpenCV's cascade classifier with OpenCV's object tracking capabilities. It allows users to automatically detect faces in a video feed and then track a selected face.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `model` directory in the project root:
```bash
mkdir model
```

3. Download the face detection model file and place it in the `model` directory:
- Download [haarcascade_frontalface_default.xml](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml)

### YOLOv3 Setup (Optional)

If you want to use YOLOv3 for more accurate face detection, download these files and place them in the `model` directory:

1. Download [YOLOv3 weights](https://pjreddie.com/media/files/yolov3.weights) (237MB)
2. Download [YOLOv3 configuration](https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg)

4. Download the yolov8 weights
- Download [best.pt](https://huggingface.co/doguilmak/Drone-Detection-YOLOv8x/tree/main/weight)

Your directory structure should now look like this:
```
project_root/
├── model/
│   ├── haarcascade_frontalface_default.xml
│   ├── yolov3.weights
│   └── yolov3.cfg
├── detection.py
├── tracking.py
├── main.py
└── requirements.txt
```

## Usage

Run the main script:
```bash
python main.py
```

### How to Use

1. The system will start in detection mode, showing detected faces with bounding boxes
2. Click on any detected face to start tracking it
3. The system will switch to tracking mode and follow the selected face
4. Press 'q' to quit the application

### Features

- Automatic face detection using OpenCV's cascade classifier
- Multiple tracking algorithms available (CSRT by default)
- Real-time FPS display
- Face center point visualization
- Smooth transition between detection and tracking modes

## Notes

- The system uses your default webcam (index 0)
- The CSRT tracker is used by default for better accuracy
- Face detection parameters are optimized for real-time performance
- Tracking will show a "Tracking failed!" message if the face is lost 