# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - Violation Tracker
# ══════════════════════════════════════════════════════════════
#
# Tracks hands across frames and detects violations.
# A violation occurs when a hand:
# 1. Enters the ROI (protein container)
# 2. Leaves the ROI WITHOUT a scooper
# 3. Goes to the pizza
#
# SKELETON VERSION - Full logic will be implemented later
#
# ══════════════════════════════════════════════════════════════

from enum import Enum
from typing import Dict, List, Optional, Tuple
import config


class HandState(Enum):
    """Possible states for a tracked hand."""
    IDLE = "idle"               # Hand not in ROI, not tracked
    IN_ROI = "in_roi"           # Hand currently inside ROI
    LEFT_ROI = "left_roi"       # Hand left ROI, tracking where it goes


class ViolationTracker:
    """
    Tracks hands and detects hygiene violations.
    
    SKELETON VERSION - Basic structure with placeholder logic.
    Full implementation coming later.
    """
    
    def __init__(self, roi: Dict = None):
        """
        Initialize the violation tracker.
        
        Args:
            roi: Region of Interest coordinates
                 {"x1": 100, "y1": 150, "x2": 400, "y2": 400}
        """
        self.roi = roi or config.DEFAULT_ROI
        
        # Track state for each hand (keyed by track_id)
        self.hand_states: Dict[int, HandState] = {}
        self.hand_had_scooper: Dict[int, bool] = {}
        self.hand_frames_since_left: Dict[int, int] = {}
        
        # Violation counter
        self.violation_count = 0
        
        # Configuration
        self.frames_to_track = config.FRAMES_TO_TRACK_AFTER_ROI
        self.proximity_margin = config.PROXIMITY_MARGIN
        
        print(f"[ViolationTracker] Initialized with ROI: {self.roi}")
    
    def process_frame(self, detections: List[Dict], frame_number: int) -> Dict:
        """
        Process detections for a single frame.
        
        Args:
            detections: List of detections from YOLO
            frame_number: Current frame number
        
        Returns:
            {
                "violation_detected": bool,
                "violation_count": int,
                "violation_details": {...} or None
            }
        
        SKELETON: Returns placeholder result.
        Full logic will be implemented later.
        """
        
        # Separate detections by class
        hands = [d for d in detections if d["class_name"] == "hand" and d.get("track_id")]
        scoopers = [d for d in detections if d["class_name"] == "scooper"]
        pizzas = [d for d in detections if d["class_name"] == "pizza"]
        
        violation_details = None
        
        # ══════════════════════════════════════════════════════════
        # TODO: Implement full violation logic here
        # For now, just return no violation
        # ══════════════════════════════════════════════════════════
        
        # Placeholder: Just track basic info
        for hand in hands:
            track_id = hand["track_id"]
            
            # Initialize tracking for new hands
            if track_id not in self.hand_states:
                self.hand_states[track_id] = HandState.IDLE
                self.hand_had_scooper[track_id] = False
                self.hand_frames_since_left[track_id] = 0
        
        return {
            "violation_detected": False,
            "violation_count": self.violation_count,
            "violation_details": violation_details
        }
    
    def update_roi(self, roi: Dict):
        """Update the ROI coordinates."""
        self.roi = roi
        print(f"[ViolationTracker] ROI updated: {self.roi}")
    
    def reset(self):
        """Reset tracker state for new video."""
        self.hand_states.clear()
        self.hand_had_scooper.clear()
        self.hand_frames_since_left.clear()
        self.violation_count = 0
        print("[ViolationTracker] Reset")
    
    # ══════════════════════════════════════════════════════════
    # HELPER METHODS (will be used by full implementation)
    # ══════════════════════════════════════════════════════════
    
    def _get_center(self, bbox: List[int]) -> Tuple[int, int]:
        """Get center point of bounding box."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def _point_in_roi(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside the ROI."""
        x, y = point
        return (self.roi["x1"] <= x <= self.roi["x2"] and
                self.roi["y1"] <= y <= self.roi["y2"])
    
    def _boxes_overlap(self, box1: List[int], box2: List[int], margin: int = 0) -> bool:
        """Check if two bounding boxes overlap (with optional margin)."""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Add margin
        x1_1 -= margin
        y1_1 -= margin
        x2_1 += margin
        y2_1 += margin
        
        return not (x2_1 < x1_2 or x2_2 < x1_1 or
                    y2_1 < y1_2 or y2_2 < y1_1)
    
    def _is_near_pizza(self, hand_bbox: List[int], pizzas: List[Dict]) -> bool:
        """Check if hand is near any pizza."""
        for pizza in pizzas:
            if self._boxes_overlap(hand_bbox, pizza["bbox"], self.proximity_margin):
                return True
        return False
    
    def _has_scooper(self, hand_bbox: List[int], scoopers: List[Dict]) -> bool:
        """Check if hand has a scooper nearby."""
        for scooper in scoopers:
            if self._boxes_overlap(hand_bbox, scooper["bbox"], self.proximity_margin):
                return True
        return False
