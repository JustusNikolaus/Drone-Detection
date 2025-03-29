import cv2
import numpy as np
import os
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, detection_type='face'):
        """
        Initialize the detector with specified type ('face' or 'yolo')
        """
        self.detection_type = detection_type
        self.model_dir = os.path.join(os.path.dirname(__file__), 'model')
        
        if detection_type == 'face':
            # Initialize face detection
            cascade_path = os.path.join(self.model_dir, "haarcascade_frontalface_default.xml")
            if not os.path.exists(cascade_path):
                raise FileNotFoundError(
                    "Face detection model file not found in the 'model' directory. "
                    "Please download and place the following file in the 'model' directory:\n"
                    "- haarcascade_frontalface_default.xml"
                )
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            self.color = (0, 255, 0)  # Green color for face detection
            
        elif detection_type == 'yolo':
            # Initialize YOLOv3
            weights_path = os.path.join(self.model_dir, "yolov3.weights")
            config_path = os.path.join(self.model_dir, "yolov3.cfg")
            names_path = os.path.join(self.model_dir, "coco.names")
            
            if not all(os.path.exists(path) for path in [weights_path, config_path, names_path]):
                raise FileNotFoundError(
                    "Required YOLOv3 files not found in the 'model' directory. "
                    "Please download and place the following files in the 'model' directory:\n"
                    "- yolov3.weights\n"
                    "- yolov3.cfg\n"
                    "- coco.names"
                )
            
            self.net = cv2.dnn.readNet(weights_path, config_path)
            with open(names_path, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
            
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        
        elif detection_type == 'yolov8':
            weights_path = os.path.join(self.model_dir, "best.pt")
            if not os.path.exists(weights_path):
                raise FileNotFoundError("YOLOv8 model file (best.pt) not found.")
            self.yolo_model = YOLO(weights_path)
            self.color = (255, 0, 0)  # Blue for YOLOv8
            
        else:
            raise ValueError("detection_type must be either 'face' or 'yolo'")
        
        print(f"Initialized {detection_type} detection")
        
    def detect(self, frame):
        """
        Detects objects/faces in the given frame and returns their bounding boxes
        """
        if self.detection_type == 'face':
            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Convert faces to the format expected by the rest of the code
            boxes = []
            confidences = []
            class_ids = []
            
            for (x, y, w, h) in faces:
                boxes.append([x, y, w, h])
                confidences.append(1.0)
                class_ids.append(0)
            
            indexes = list(range(len(boxes)))
            
        elif self.detection_type == 'yolo':  # YOLOv3 detection
            height, width, _ = frame.shape
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
            
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)
            
            class_ids = []
            confidences = []
            boxes = []
            
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.3:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.3)
        
        elif self.detection_type == 'yolov8':
            results = self.yolo_model.predict(frame, imgsz=640, conf=0.3, verbose=False)
            boxes = []
            confidences = []
            class_ids = []

            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    boxes.append([x1, y1, x2 - x1, y2 - y1])
                    confidences.append(conf)
                    class_ids.append(class_id)

            indexes = list(range(len(boxes)))

        return boxes, confidences, class_ids, indexes
    
    def draw_detections(self, frame, boxes, confidences, class_ids, indexes):
        """
        Draws the detected objects/faces on the frame
        """
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                if self.detection_type == 'face':
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, 2)
                    cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.color, 2)
                elif self.detection_type == 'yolo':
                    label = str(self.classes[class_ids[i]])
                    color = self.colors[class_ids[i]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label} {confidences[i]:.2f}", (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                elif self.detection_type == 'yolov8':
                    for i in range(len(boxes)):
                        if i in indexes:
                            x, y, w, h = boxes[i]
                            label = str(class_ids[i])
                            if hasattr(self.yolo_model, "names"):
                                label = self.yolo_model.names.get(class_ids[i], str(class_ids[i]))
                            cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, 2)
                            cv2.putText(frame, f"{label} {confidences[i]:.2f}", (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.color, 2)

        
        return frame
    
    def get_clicked_object(self, event, x, y, flags, param):
        """
        Callback function for mouse click events
        Returns the clicked object's bounding box if clicked on a detection
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            boxes, confidences, class_ids, indexes = param
            for i in range(len(boxes)):
                if i in indexes:
                    box_x, box_y, box_w, box_h = boxes[i]
                    if (box_x <= x <= box_x + box_w and 
                        box_y <= y <= box_y + box_h):
                        return (box_x, box_y, box_w, box_h)
        return None 