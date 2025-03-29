import cv2
import time
from Attitude import Attitude
from CompanionController import ConstantRateController
from UnitConverter import UnitConverter
import traceback
from detection import ObjectDetector
from tracking import ObjectTracker
from terminal_utils import (
    print_header, print_success, print_warning, print_error, 
    print_info, print_loading, print_menu, print_status
)

class ObjectTrackingSystem:
    def __init__(self, detection_type='face'):
        """
        Initialize the tracking system with specified detection type
        Args:
            detection_type: 'face' or 'yolo'
        """
        try:
            print_header("Object Tracking System")
            print_loading(f"Initializing {detection_type} detection system...", 1.5)
            self.detector = ObjectDetector(detection_type)
            self.tracker = None
            self.tracking = False
            self.selected_bbox = None
            self.attitude = Attitude()
            self.controller = ConstantRateController(UnitConverter())
            
            # Initialize video capture with more detailed error checking
            print_info("Attempting to open video capture device...")
            self.video = cv2.VideoCapture(0)
            
            # Check if camera opened successfully
            if not self.video.isOpened():
                print_error("Failed to open camera. Please check camera permissions.")
                print_info("On macOS, please ensure camera access is granted in System Preferences > Security & Privacy > Privacy > Camera")
                raise Exception("Could not open video capture device")
            
            # Initialize height and width of video
            ret, frame = self.video.read()
            self.height, self.width = frame.shape[:2]
            
            if not ret:
                print_error("Camera opened but failed to read frame. Please check camera permissions.")
                print_info("On macOS, please ensure camera access is granted in System Preferences > Security & Privacy > Privacy > Camera")
                raise Exception("Could not read frame from camera")
                
            print_success("Video capture device opened successfully")
            
        except Exception as e:
            print_error(f"Error during initialization: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise
    
    def mouse_callback(self, event, x, y, flags, param):
        """
        Handle mouse events for object selection
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.tracking:
                print_warning("Stopping tracking")
                # If we're tracking, stop tracking
                self.stop_tracking()
            else:
                # If we're not tracking, try to start tracking
                print_info("Starting tracking")
                bbox = self.detector.get_clicked_object(event, x, y, flags, param)
                if bbox is not None:
                    self.start_tracking(bbox)

    def run(self):
        """
        Main loop for the object detection and tracking system
        """
        try:
            # Start attitude receiver thread
            self.attitude.start_receiving()
            
            # Create window at startup
            cv2.namedWindow('Detection', cv2.WINDOW_NORMAL)
            print_info("Press 'q' to quit the application")
            
            while True:
                ok, frame = self.video.read()
                if not ok:
                    print_error("Failed to read frame from video capture")
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
                    
                    # Set and get attitude
                    self.attitude.set_attitude()
                    roll, pitch, yaw = self.attitude.get_attitude()
                    
                    # Calculate coordinates and draw tracking
                    p1, p2, center_box = self.tracker.calculate_coordinates(success, bbox)
                    frame = self.tracker.draw_tracking(frame, fps, p1, p2, center_box)
                    
                    # Calculate x_error and x_yaw_rate
                    x_error = center_box[0] - (self.width / 2)
                    # use x_error to calculate new x_yaw_rate 
                    x_yaw_rate = self.controller.compute_control(x_error)
                    self.attitude.send_attitude(roll = roll, pitch = pitch, yaw = x_yaw_rate)

                    # Set up mouse callback for object selection
                    cv2.setMouseCallback('Tracking', self.mouse_callback, 
                                      (success, bbox, fps))
                    
                    cv2.imshow('Tracking', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except Exception as e:
            print_error(f"Error during tracking: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
        finally:
            # Cleanup
            self.cleanup()
    
    def cleanup(self):
        """ Clean up resources and stop threads """
        print_info("Cleaning up resources...")
        
        # Stop attitude threads
        self.attitude.stop_receiving()
        
        # Release video capture
        if self.video:
            self.video.release()
        
        # Close all windows
        cv2.destroyAllWindows()
        
        print_success("Cleanup completed")
    
    def start_tracking(self, bbox):
        """
        Initialize tracking for the selected bounding box
        """
        self.tracker = ObjectTracker()
        self.tracker.init(self.video.read()[1], bbox)
        self.tracking = True
        self.selected_bbox = bbox
        # Create tracking window and destroy detection window
        print_info("Switching to tracking mode...")
        cv2.destroyWindow('Detection')
        cv2.namedWindow('Tracking')
        print_success("Tracking started")

    def stop_tracking(self):
        """
        Stop tracking the selected object
        """
        self.tracking = False
        # Create detection window and destroy tracking window
        print_info("Switching back to detection mode...")
        cv2.destroyWindow('Tracking')
        cv2.namedWindow('Detection')
        print_success("Tracking stopped")
        

def main():
    try:
        # Ask user for detection type
        print_menu(
            ["Face Detection", "YOLOv3 Detection", "YOLOv8 Detection"],
            "Select Detection Type"
        )
        
        while True:
            try:
                choice = int(input("\nEnter your choice (1-3): "))
                if 1 <= choice <= 3:
                    break
                print_warning("Please enter a number between 1 and 3")
            except ValueError:
                print_error("Please enter a valid number")
        
        detection_types = ['face', 'yolo', 'yolov8']
        detection_type = detection_types[choice - 1]
        
        print_status(f"Starting system with {detection_type} detection...", "info")
        system = ObjectTrackingSystem(detection_type)
        system.run()
    except Exception as e:
        print_error(f"Fatal error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 