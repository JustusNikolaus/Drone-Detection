import cv2
from detection import ObjectDetector
import os

def main():
    # Initialize the detector with YOLOv8
    detector = ObjectDetector(detection_type='yolov8')
    
    # Get the video file path
    video_path = os.path.join('videos', 'short_meet.mp4')
    
    # Open the video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return
    
    # Initialize variables to track detection
    frame_count = 0
    objects_detected = False
    first_detection_frame = None
    
    print("Processing video...")
    print("Press ENTER to advance to next frame when objects are detected")
    
    while True:
        # Read frame from video
        ret, frame = cap.read()
        if not ret:
            break
            
        # Detect objects in the frame
        boxes, confidences, class_ids, indexes = detector.detect(frame)
        
        # Check if any objects were detected in this frame
        if len(boxes) > 0:
            objects_detected = True
            if first_detection_frame is None:
                first_detection_frame = frame_count
                print(f"First object detected at frame {frame_count}")
        
            # Draw detections on the frame
            frame = detector.draw_detections(frame, boxes, confidences, class_ids, indexes)
            
            # Display the frame
            cv2.imshow('YOLOv8 Detection', frame)
            
            # Wait for ENTER key (ASCII code 13) when objects are detected
            while True:
                key = cv2.waitKey(0)
                if key == 13:  # ENTER key
                    break
                elif key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
        else:
            # If no objects detected, show frame briefly
            cv2.imshow('YOLOv8 Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        frame_count += 1
    
    # Print final results
    print("\nDetection Results:")
    print(f"Objects detected: {objects_detected}")
    if first_detection_frame is not None:
        print(f"First detection occurred at frame: {first_detection_frame}")
    print(f"Total frames processed: {frame_count}")
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 