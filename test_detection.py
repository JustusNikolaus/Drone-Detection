import cv2
from detection import ObjectDetector
import os
from terminal_utils import print_info, print_success, print_warning, print_error, print_status, print_header

def main():
    # Initialize the detector with YOLOv8
    detector = ObjectDetector(detection_type='yolov8')
    
    # Get the video file path
    video_path = "test_video.mp4"
    if not os.path.exists(video_path):
        print_error(f"Could not open video file at {video_path}")
        return
    
    # Open the video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print_error("Failed to open video capture")
        return
    
    # Initialize variables to track detection
    frame_count = 0
    objects_detected = 0
    first_detection_frame = None
    
    print_info("Processing video...")
    print_info("Press ENTER to advance to next frame when objects are detected")
    
    while True:
        # Read frame from video
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        detections = detector.detect(frame)
        
        if detections:
            objects_detected += 1
            if first_detection_frame is None:
                first_detection_frame = frame_count
                print_success(f"First object detected at frame {frame_count}")
            
            # Draw bounding boxes and labels
            for detection in detections:
                bbox = detection['bbox']
                label = detection['label']
                confidence = detection['confidence']
                
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        # Display the frame
        cv2.imshow('Detection Test', frame)
        
        # Wait for ENTER key (ASCII code 13) when objects are detected
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    print_header("\nDetection Results")
    print_info(f"Objects detected: {objects_detected}")
    if first_detection_frame:
        print_info(f"First detection occurred at frame: {first_detection_frame}")
    print_info(f"Total frames processed: {frame_count}")

if __name__ == "__main__":
    main() 