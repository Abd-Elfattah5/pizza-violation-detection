# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - Main Entry Point
# ══════════════════════════════════════════════════════════════
#
# Orchestrates the detection pipeline:
# 1. Consume frames from RabbitMQ
# 2. Run YOLO detection with tracking
# 3. Check for violations
# 4. Publish processed frames
# 5. Save violations to database
#
# SKELETON VERSION - Basic structure ready for full implementation
#
# ══════════════════════════════════════════════════════════════

import sys
import os
import base64
import cv2
import numpy as np

import config
from consumer import FrameConsumer
from publisher import ProcessedFramePublisher
from detector import Detector
from violation_tracker import ViolationTracker
from database import Database


class DetectionService:
    """
    Main Detection Service class.
    """
    
    def __init__(self):
        self.consumer = FrameConsumer()
        self.publisher = ProcessedFramePublisher()
        self.detector = Detector()
        self.violation_tracker = ViolationTracker()
        self.database = Database()
        
        self.current_video_id = None
        self.frames_processed = 0
    
    def initialize(self) -> bool:
        """Initialize all components."""
        print("\n" + "=" * 60)
        print("DETECTION SERVICE - Initializing")
        print("=" * 60 + "\n")
        
        config.print_config()
        
        # Load YOLO model
        if not self.detector.load_model():
            return False
        
        # Connect to RabbitMQ (consumer)
        if not self.consumer.connect():
            return False
        
        # Connect to RabbitMQ (publisher)
        if not self.publisher.connect():
            return False
        
        # Connect to database
        if not self.database.connect():
            return False
        
        # Load ROI from database
        rois = self.database.get_active_rois()
        if rois:
            self.violation_tracker.update_roi(rois[0]['coordinates'])
        
        print("\n" + "=" * 60)
        print("DETECTION SERVICE - Ready!")
        print("=" * 60 + "\n")
        
        return True
    
    def process_frame(self, frame_data: dict) -> dict:
        """
        Process a single frame.
        
        Args:
            frame_data: Message from RabbitMQ containing:
                - video_id
                - frame_number
                - timestamp
                - frame_data (base64 encoded JPEG)
                - width, height, fps, etc.
        
        Returns:
            Processing result dict
        """
        
        # Track video changes
        video_id = frame_data.get("video_id")
        if video_id != self.current_video_id:
            self._handle_new_video(frame_data)
        
        frame_number = frame_data.get("frame_number", 0)
        timestamp = frame_data.get("timestamp", 0.0)
        
        # Decode frame
        frame_bytes = base64.b64decode(frame_data["frame_data"])
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            print(f"[Service] ❌ Failed to decode frame {frame_number}")
            return {"success": False}
        
        # Run detection with tracking
        detections = self.detector.detect_with_tracking(frame)
        
        # Check for violations
        violation_result = self.violation_tracker.process_frame(detections, frame_number)
        
        # Handle violation if detected
        if violation_result["violation_detected"]:
            self._handle_violation(
                video_id=video_id,
                frame_number=frame_number,
                timestamp=timestamp,
                frame=frame,
                detections=detections,
                violation_details=violation_result["violation_details"]
            )
        
        # Draw detections on frame
        annotated_frame = self.detector.draw_detections(
            frame=frame,
            detections=detections,
            roi=self.violation_tracker.roi,
            violation=violation_result["violation_detected"]
        )
        
        # Encode annotated frame
        _, encoded = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_bytes = encoded.tobytes()
        
        # Publish processed frame
        self.publisher.publish_processed_frame(
            frame_bytes=annotated_bytes,
            metadata={
                "video_id": video_id,
                "frame_number": frame_number,
                "timestamp": timestamp,
                "detections": detections,
                "violation_detected": violation_result["violation_detected"],
                "violation_count": violation_result["violation_count"]
            }
        )
        
        self.frames_processed += 1
        
        # Update progress every 30 frames
        if self.frames_processed % 30 == 0:
            self.database.update_video_progress(video_id, self.frames_processed)
        
        return {
            "success": True,
            "frame_number": frame_number,
            "detections_count": len(detections),
            "violation_detected": violation_result["violation_detected"]
        }
    
    def _handle_new_video(self, frame_data: dict):
        """Handle when a new video starts processing."""
        video_id = frame_data.get("video_id")
        
        print(f"\n[Service] New video: {video_id}")
        
        # Reset tracker for new video
        self.violation_tracker.reset()
        
        # Create video record in database
        self.database.create_video(
            video_id=video_id,
            filename=frame_data.get("filename", "unknown"),
            filepath=frame_data.get("filepath", ""),
            total_frames=frame_data.get("total_frames", 0),
            fps=frame_data.get("fps", 30),
            width=frame_data.get("width", 0),
            height=frame_data.get("height", 0),
            duration=frame_data.get("total_frames", 0) / frame_data.get("fps", 30)
        )
        
        self.current_video_id = video_id
        self.frames_processed = 0
    
    def _handle_violation(self, video_id: str, frame_number: int, timestamp: float,
                         frame: np.ndarray, detections: list, violation_details: dict):
        """Handle a detected violation."""
        
        print(f"[Service] 🚨 VIOLATION at frame {frame_number}!")
        
        # Save frame image
        frame_path = None
        if config.SAVE_VIOLATION_FRAMES:
            frame_dir = os.path.join(config.VIOLATIONS_DIR, video_id)
            os.makedirs(frame_dir, exist_ok=True)
            frame_path = os.path.join(frame_dir, f"frame_{frame_number}.jpg")
            cv2.imwrite(frame_path, frame)
        
        # Save to database
        self.database.save_violation(
            video_id=video_id,
            frame_number=frame_number,
            timestamp=timestamp,
            frame_path=frame_path,
            bbox_data=violation_details or {},
            description="Hand grabbed from ROI without scooper and placed on pizza"
        )
    
    def run(self):
        """Start the detection service."""
        print("[Service] Starting frame consumption...")
        self.consumer.start_consuming(callback=self.process_frame)
    
    def shutdown(self):
        """Clean shutdown."""
        print("\n[Service] Shutting down...")
        
        # Mark current video as completed
        if self.current_video_id:
            self.database.update_video_completed(
                self.current_video_id,
                self.violation_tracker.violation_count
            )
        
        self.consumer.close()
        self.publisher.close()
        self.database.close()
        print("[Service] Shutdown complete")


def main():
    """Main entry point."""
    service = DetectionService()
    
    if not service.initialize():
        print("[Main] ❌ Failed to initialize service")
        sys.exit(1)
    
    try:
        service.run()
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user")
    except Exception as e:
        print(f"[Main] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.shutdown()


if __name__ == "__main__":
    main()
