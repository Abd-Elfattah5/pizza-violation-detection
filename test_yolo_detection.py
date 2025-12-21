# ══════════════════════════════════════════════════════════════
# TEST SCRIPT - YOLO Detection on Video Frame
# ══════════════════════════════════════════════════════════════

import cv2
import os
from ultralytics import YOLO

def test_yolo():
    """Test YOLO detection on a video frame."""
    
    model_path = "services/detection/models/yolo_model.pt"
    video_dir = "videos"
    
    # Load model
    print(f"\n{'='*60}")
    print("YOLO DETECTION TEST")
    print(f"{'='*60}\n")
    
    print("Loading model...")
    model = YOLO(model_path)
    print(f"✅ Model loaded: {model_path}")
    print(f"   Classes: {model.names}\n")
    
    # Find video
    video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.mkv'))]
    if not video_files:
        print("❌ No videos found")
        return False
    
    video_path = os.path.join(video_dir, video_files[0])
    print(f"Testing on: {video_path}\n")
    
    # Read first frame
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Could not read frame")
        return False
    
    print(f"Frame shape: {frame.shape}")
    
    # Run detection
    print("\nRunning detection...")
    results = model(frame, verbose=False)
    
    # Parse results
    print("\nDetections:")
    print("-" * 40)
    
    detections = []
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        bbox = box.xyxy[0].tolist()
        
        detections.append({
            "class": class_name,
            "confidence": confidence,
            "bbox": bbox
        })
        
        print(f"  {class_name}: {confidence:.2f} at {[int(x) for x in bbox]}")
    
    if not detections:
        print("  (No objects detected in this frame)")
    
    print("-" * 40)
    print(f"\nTotal detections: {len(detections)}")
    
    # Test tracking mode
    print("\nTesting TRACKING mode...")
    results_track = model.track(frame, persist=True, verbose=False)
    
    track_count = 0
    for box in results_track[0].boxes:
        if box.id is not None:
            track_id = int(box.id[0])
            class_name = model.names[int(box.cls[0])]
            print(f"  Track ID {track_id}: {class_name}")
            track_count += 1
    
    if track_count == 0:
        print("  (No tracks in single frame - normal)")
    
    print(f"\n{'='*60}")
    print("🎉 YOLO DETECTION TEST PASSED!")
    print(f"{'='*60}\n")
    
    return True

if __name__ == "__main__":
    success = test_yolo()
    exit(0 if success else 1)
