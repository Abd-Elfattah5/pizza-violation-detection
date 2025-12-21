# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - YOLO Detector
# ══════════════════════════════════════════════════════════════
#
# Handles YOLO model loading and inference
#
# ══════════════════════════════════════════════════════════════

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import config


class Detector:
    """
    YOLO object detector wrapper.
    
    Detects: hand, person, pizza, scooper
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to YOLO model file (.pt)
        """
        self.model_path = model_path or config.MODEL_PATH
        self.model = None
        self.class_names = {}
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
    
    def load_model(self) -> bool:
        """Load the YOLO model."""
        try:
            print(f"[Detector] Loading model: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.class_names = self.model.names
            print(f"[Detector] ✅ Model loaded!")
            print(f"[Detector]    Classes: {self.class_names}")
            return True
        except Exception as e:
            print(f"[Detector] ❌ Failed to load model: {e}")
            return False
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Run detection on a single frame.
        
        Args:
            frame: BGR image (numpy array)
        
        Returns:
            List of detections:
            [
                {
                    "class_id": 0,
                    "class_name": "hand",
                    "confidence": 0.92,
                    "bbox": [x1, y1, x2, y2]
                },
                ...
            ]
        """
        if self.model is None:
            print("[Detector] ❌ Model not loaded!")
            return []
        
        # Run inference
        results = self.model(
            frame, 
            conf=self.confidence_threshold,
            verbose=False
        )
        
        # Parse results
        detections = []
        for box in results[0].boxes:
            detection = {
                "class_id": int(box.cls[0]),
                "class_name": self.class_names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": [int(x) for x in box.xyxy[0].tolist()]
            }
            detections.append(detection)
        
        return detections
    
    def detect_with_tracking(self, frame: np.ndarray) -> List[Dict]:
        """
        Run detection with object tracking.
        Assigns persistent IDs to objects across frames.
        
        Args:
            frame: BGR image (numpy array)
        
        Returns:
            List of detections with track IDs:
            [
                {
                    "class_id": 0,
                    "class_name": "hand",
                    "confidence": 0.92,
                    "bbox": [x1, y1, x2, y2],
                    "track_id": 1
                },
                ...
            ]
        """
        if self.model is None:
            print("[Detector] ❌ Model not loaded!")
            return []
        
        # Run inference with tracking
        results = self.model.track(
            frame,
            conf=self.confidence_threshold,
            persist=True,  # Maintain track IDs across frames
            verbose=False
        )
        
        # Parse results
        detections = []
        for box in results[0].boxes:
            detection = {
                "class_id": int(box.cls[0]),
                "class_name": self.class_names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": [int(x) for x in box.xyxy[0].tolist()],
                "track_id": int(box.id[0]) if box.id is not None else None
            }
            detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict], 
                        roi: Dict = None, violation: bool = False) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: BGR image
            detections: List of detections
            roi: ROI coordinates to draw (optional)
            violation: If True, add violation indicator
        
        Returns:
            Frame with drawings
        """
        frame_copy = frame.copy()
        
        # Color mapping for classes
        colors = {
            "hand": (0, 255, 255),      # Yellow
            "person": (255, 0, 0),       # Blue
            "pizza": (0, 165, 255),      # Orange
            "scooper": (0, 255, 0)       # Green
        }
        
        # Draw ROI if provided
        if roi:
            cv2.rectangle(
                frame_copy,
                (roi["x1"], roi["y1"]),
                (roi["x2"], roi["y2"]),
                (0, 255, 0),  # Green
                2
            )
            cv2.putText(
                frame_copy,
                "ROI",
                (roi["x1"], roi["y1"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        # Draw detections
        for det in detections:
            bbox = det["bbox"]
            class_name = det["class_name"]
            confidence = det["confidence"]
            track_id = det.get("track_id")
            
            color = colors.get(class_name, (255, 255, 255))
            
            # Draw box
            cv2.rectangle(
                frame_copy,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                color,
                2
            )
            
            # Draw label
            label = f"{class_name}"
            if track_id:
                label += f" #{track_id}"
            label += f" {confidence:.2f}"
            
            cv2.putText(
                frame_copy,
                label,
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        # Draw violation indicator
        if violation:
            cv2.putText(
                frame_copy,
                "VIOLATION DETECTED!",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),  # Red
                3
            )
            # Add red border
            cv2.rectangle(
                frame_copy,
                (5, 5),
                (frame_copy.shape[1] - 5, frame_copy.shape[0] - 5),
                (0, 0, 255),
                5
            )
        
        return frame_copy
