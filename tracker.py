import cv2
# from picamera2 import Picamera2
import time

from UnitConverter import UnitConverter
from Attitude import Attitude
from CompanionController import ConstantRateController
from CompanionController import ProportionalController

#setup and initialize Picamer2
# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration(raw={"size":(1640,1232)},main={"format":'RGB888',"size": (640,480)}))
# picam2.start()
# time.sleep(2)

# used to record the time when we processed last frame 
prev_frame_time = 0
new_frame_time = 0

# font which we will be using to display FPS 
font = cv2.FONT_HERSHEY_SIMPLEX


# Define and initialize  the tracker type (you can change it to others like 'KCF', 'CSRT', etc.)
tracker_zoo = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
tracker_type = tracker_zoo[7]
print("Tracker selected:",  tracker_type)

#CPU unilization on laptop with intel ultra7
if tracker_type == 'BOOSTING': # cpu ~15%, track after reappear: yes, detect lost target: no
    tracker = cv2.legacy.TrackerBoosting_create()
if tracker_type == 'MIL':   # cpu ~90%, track after reappear: yes, detect lost target: no
    tracker = cv2.TrackerMIL_create()
if tracker_type == 'KCF': # cpu ~5%, track after reappear: sometimes, detect lost target: yes, Note: chanse lost after zoom
    tracker = cv2.TrackerKCF_create()
if tracker_type == 'TLD': # cpu ~60-75%, track after reappear: yes, detect lost target: yes
    tracker = cv2.legacy.TrackerTLD_create()
if tracker_type == 'MEDIANFLOW': # cpu ~15-20%, track after reappear: yes, detect lost target: no
    tracker = cv2.legacy.TrackerMedianFlow_create()
if tracker_type == 'GOTURN':
    tracker = cv2.TrackerGOTURN_create()
if tracker_type == 'MOSSE':# cpu ~1-2.5%, track after reappear: yes, detect lost target: no
    tracker = cv2.legacy.TrackerMOSSE_create()
if tracker_type == "CSRT": # cpu ~35%, track after reappear: yes, detect lost target: no
    tracker = cv2.TrackerCSRT_create()


# start video stream to select tracking object Raspberry
# while True:
#     frame = picam2.capture_array()
#     cv2.imshow("ROI selection", frame)
#     if cv2.waitKey(1) & 0xFF == ord(' '):
#         break

# start video stream to select tracking object webcam
video = cv2.VideoCapture(0)

while True:
    k,frame = video.read()
    cv2.imshow("ROI selection", frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break


height, width = frame.shape[:2]
print("Video resolution height:", height)
print("Video resolution width:", width)
    
# select boundig box by pressing esc and then the space bar to exit
bbox = cv2.selectROI(frame, False)
tracker.init(frame, bbox)
cv2.destroyWindow('ROI selection')


prev_frame_time = time.time()

# EDIT: initiate Attitude class; start receiving; init controller of choice
attitude = Attitude()
attitude.start_receiving()
controller = ConstantRateController(UnitConverter())

# continue video feed while tracking object
while True:
    ok, frame = video.read()
    _, bbox = tracker.update(frame)

    # EDIT: store latest attitude here for minimal latency
    attitude.set_attitude()
    roll, pitch, yaw = attitude.get_attitude()

    # draw bbox
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (0,0,255),2,2)
    #calculate and draw centerpoint of bbox
    center_bbox = [int(bbox[0])+int(bbox[2]/2),int(bbox[1])+int(bbox[3]/2)]
    print(center_bbox)
    cv2.circle(frame,(center_bbox[0],center_bbox[1]),3,(0,0,255),2)
    
    # EDIT: calculate new attitude using center_bbox
    x_error = center_bbox[0] - (width / 2)
                                        # use x_error to calculate new x_yaw_rate 
    x_yaw_rate = controller.compute_control(x_error)
    attitude.send_attitude(roll = roll, pitch = pitch, yaw = x_yaw_rate)


    #calculate frame rate and burn it
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = round(fps,1)
    fps = str(fps) 
    cv2.putText(frame, fps, (7, 70), font, 2, (100, 255, 0), 3, cv2.LINE_AA)
    
    
    cv2.imshow('Tracking',frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

# Release resources
# picam2.stop()
# picam2.close()
cv2.destroyAllWindows()