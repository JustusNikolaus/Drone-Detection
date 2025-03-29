import cv2
import time
import traceback
from detection import ObjectDetector
from tracking import ObjectTracker

class ObjectTrackingSystem:
    def __init__(self, detection_type='face'):
        """
        Initialize the tracking system with specified detection type
        Args:
            detection_type: 'face' or 'yolo'
        """
        try:
            print(f"Initializing {detection_type} detection system...")
            self.detector = ObjectDetector(detection_type)
            self.tracker = None
            self.tracking = False
            self.selected_bbox = None
            
            # Initialize video capture
            print("Attempting to open video capture device...")
            self.video = cv2.VideoCapture(0)
            if not self.video.isOpened():
                raise Exception("Could not open video capture device")
            print("Video capture device opened successfully")
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise
    
    def mouse_callback(self, event, x, y, flags, param):
        """
        Handle mouse events for object selection
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.tracking:
                print("Stopping tracking")
                # If we're tracking, stop tracking
                self.stop_tracking()
            else:
                # If we're not tracking, try to start tracking
                print("Starting tracking")
                bbox = self.detector.get_clicked_object(event, x, y, flags, param)
                if bbox is not None:
                    self.start_tracking(bbox)

    def run(self):
        """
        Main loop for the object detection and tracking system
        """
        try:
            # Create only the detection window at startup
            cv2.namedWindow('Detection')
            
            while True:
                ok, frame = self.video.read()
                if not ok:
                    break
                    
                if not self.tracking:
                    # Detection mode
                    boxes, confidences, class_ids, indexes = self.detector.detect(frame)
                    frame = self.detector.draw_detections(frame, boxes, confidences, class_ids, indexes)
                    
                    # Set up mouse callback for object selection
                    cv2.setMouseCallback('Detection', self.mouse_callback, 
                                      (boxes, confidences, class_ids, indexes))
                    
                    cv2.imshow('Detection', frame)
                    
                    # Wait for key press
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                        
                else:
                    # Tracking mode
                    success, bbox, fps = self.tracker.update(frame)
                    frame = self.tracker.draw_tracking(frame, success, bbox, fps)
                    
                    # Set up mouse callback for object selection
                    cv2.setMouseCallback('Tracking', self.mouse_callback, 
                                      (success, bbox, fps))
                    
                    cv2.imshow('Tracking', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    
        finally:
            self.video.release()
            cv2.destroyAllWindows()
    
    def start_tracking(self, bbox):
        """
        Initialize tracking for the selected bounding box
        """
        self.tracker = ObjectTracker()
        self.tracker.init(self.video.read()[1], bbox)
        self.tracking = True
        self.selected_bbox = bbox
        # Create tracking window and destroy detection window
        print("Destroying Detection window, creating Tracking window")
        cv2.destroyWindow('Detection')
        cv2.namedWindow('Tracking')
        print("Tracking started")

    def stop_tracking(self):
        """
        Stop tracking the selected object
        """
        self.tracking = False
        # Create detection window and destroy tracking window
        print("Destroying Tracking window, creating Detection window")
        cv2.destroyWindow('Tracking')
        cv2.namedWindow('Detection')
        print("Tracking stopped")
        

def main():
    try:
        # Ask user for detection type
        while True:
            detection_type = input("Choose detection type (face/yolo): ").lower()
            if detection_type in ['face', 'yolo', 'yolov8']:
                break
            print("Please enter either 'face' or 'yolo'")
        
        print(f"Starting system with {detection_type} detection...")
        system = ObjectTrackingSystem(detection_type)
        system.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 