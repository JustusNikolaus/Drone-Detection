import cv2
# from picamera2 import Picamera2
import time
from terminal_utils import print_info, print_warning, print_error

#setup and initialize Picamer2
# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration(raw={"size":(1640,1232)},main={"format":'RGB888',"size": (640,480)}))
# picam2.start()
# time.sleep(2)

#CPU unilization on laptop with intel ultra7
# if tracker_type == 'BOOSTING': # cpu ~15%, track after reappear: yes, detect lost target: no
#     tracker = cv2.legacy.TrackerBoosting_create()
# if tracker_type == 'MIL':   # cpu ~90%, track after reappear: yes, detect lost target: no
#     tracker = cv2.TrackerMIL_create()
# if tracker_type == 'KCF': # cpu ~5%, track after reappear: sometimes, detect lost target: yes, Note: chanse lost after zoom
#     tracker = cv2.TrackerKCF_create()
# if tracker_type == 'TLD': # cpu ~60-75%, track after reappear: yes, detect lost target: yes
#     tracker = cv2.legacy.TrackerTLD_create()
# if tracker_type == 'MEDIANFLOW': # cpu ~15-20%, track after reappear: yes, detect lost target: no
#     tracker = cv2.legacy.TrackerMedianFlow_create()
# if tracker_type == 'GOTURN':
#     tracker = cv2.TrackerGOTURN_create()
# if tracker_type == 'MOSSE':# cpu ~1-2.5%, track after reappear: yes, detect lost target: no
#     tracker = cv2.legacy.TrackerMOSSE_create()
# if tracker_type == "CSRT": # cpu ~35%, track after reappear: yes, detect lost target: no
#     tracker = cv2.TrackerCSRT_create()

# used to record the time when we processed last frame 
prev_frame_time = 0
new_frame_time = 0

# font which we will be using to display FPS 
font = cv2.FONT_HERSHEY_SIMPLEX

class ObjectTracker:
    def __init__(self, tracker_type='CSRT'):
        # Define available tracker types with their characteristics
        self.tracker_zoo = {
            'BOOSTING': {  # cpu ~15%
                'create': cv2.legacy.TrackerBoosting_create,
                'track_after_reappear': True,
                'detect_lost': False
            },
            'MIL': {  # cpu ~90%
                'create': cv2.TrackerMIL_create,
                'track_after_reappear': True,
                'detect_lost': False
            },
            'KCF': {  # cpu ~5%
                'create': cv2.TrackerKCF_create,
                'track_after_reappear': 'sometimes',
                'detect_lost': True
            },
            'TLD': {  # cpu ~60-75%
                'create': cv2.legacy.TrackerTLD_create,
                'track_after_reappear': True,
                'detect_lost': True
            },
            'MEDIANFLOW': {  # cpu ~15-20%
                'create': cv2.legacy.TrackerMedianFlow_create,
                'track_after_reappear': True,
                'detect_lost': False
            },
            'GOTURN': {
                'create': cv2.TrackerGOTURN_create,
                'track_after_reappear': False,
                'detect_lost': False
            },
            'MOSSE': {  # cpu ~1-2.5%
                'create': cv2.legacy.TrackerMOSSE_create,
                'track_after_reappear': True,
                'detect_lost': False
            },
            'CSRT': {  # cpu ~35%
                'create': cv2.TrackerCSRT_create,
                'track_after_reappear': False,
                'detect_lost': False
            }
        }
        
        # Initialize tracker type
        if tracker_type not in self.tracker_zoo:
            raise ValueError(f"Unknown tracker type: {tracker_type}")
        self.tracker_type = tracker_type
        print_info(f"Tracker selected: {tracker_type}")
        
        # Initialize tracker
        self.tracker = self.create_tracker(tracker_type)
        
        # Performance metrics
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def create_tracker(self, tracker_type):
        """
        Creates and returns a tracker instance based on the specified type
        """
        return self.tracker_zoo[tracker_type]['create']()
    
    def init(self, frame, bbox):
        """
        Initialize the tracker with a frame and bounding box
        """
        self.tracker.init(frame, bbox)
        self.prev_frame_time = time.time()
    
    def update(self, frame):
        """
        Update the tracker with a new frame
        Returns:
            success: bool, whether tracking was successful
            bbox: tuple, the bounding box coordinates (x, y, w, h)
            fps: float, current frames per second
        """
        success, bbox = self.tracker.update(frame)
        
        # Calculate FPS
        self.new_frame_time = time.time()
        fps = 1/(self.new_frame_time - self.prev_frame_time)
        self.prev_frame_time = self.new_frame_time
        fps = round(fps, 1)
        
        return success, bbox, fps
    
    def draw_tracking(self, frame, success, bbox, fps):
        """
        Draw the tracking box and FPS on the frame
        """
        if success:
            # Draw bbox
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0,0,255), 2, 2)
            
            # Calculate and draw centerpoint of bbox
            center_bbox = [int(bbox[0])+int(bbox[2]/2), int(bbox[1])+int(bbox[3]/2)]
            cv2.circle(frame, (center_bbox[0], center_bbox[1]), 3, (0,0,255), 2)
        else:
            cv2.putText(frame, "Tracking failed!", (100, 80), self.font, 
                       0.75, (0, 0, 255), 2)
            print_warning("Tracking lost target!")
        
        # Draw FPS
        cv2.putText(frame, str(fps), (7, 70), self.font, 2, (100, 255, 0), 3, cv2.LINE_AA)
        
        return frame
