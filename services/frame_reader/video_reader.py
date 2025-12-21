# ══════════════════════════════════════════════════════════════
# FRAME READER SERVICE - Video Reader
# ══════════════════════════════════════════════════════════════

import cv2
import os
from typing import Generator, Tuple, Optional
import config


class VideoReader:
    """Reads video files frame by frame using OpenCV."""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap: Optional[cv2.VideoCapture] = None
        self.width: int = 0
        self.height: int = 0
        self.fps: float = 0.0
        self.total_frames: int = 0
        self.duration: float = 0.0
    
    def open(self) -> bool:
        """Open the video file."""
        if not os.path.exists(self.video_path):
            print(f"[VideoReader] ❌ File not found: {self.video_path}")
            return False
        
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print(f"[VideoReader] ❌ Could not open: {self.video_path}")
            return False
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0.0
        
        print(f"[VideoReader] ✅ Opened: {self.video_path}")
        print(f"[VideoReader]    {self.width}x{self.height} @ {self.fps}fps")
        print(f"[VideoReader]    {self.total_frames} frames, {self.duration:.2f}s")
        return True
    
    def read_frames(self) -> Generator[Tuple[int, float, any], None, None]:
        """Generator that yields frames one by one."""
        if not self.cap or not self.cap.isOpened():
            print("[VideoReader] ❌ Video not opened!")
            return
        
        frame_number = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print(f"[VideoReader] Finished. Frames: {frame_number}")
                break
            
            if frame_number % config.FRAME_SKIP != 0:
                frame_number += 1
                continue
            
            timestamp = frame_number / self.fps if self.fps > 0 else 0.0
            yield frame_number, timestamp, frame
            frame_number += 1
            
            if frame_number % 100 == 0:
                progress = (frame_number / self.total_frames) * 100
                print(f"[VideoReader] Progress: {progress:.1f}%")
    
    def encode_frame(self, frame, quality = None) -> bytes:
        """Encode a frame as JPEG bytes."""
        if quality is None:
            quality = config.JPEG_QUALITY
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        success, encoded = cv2.imencode('.jpg', frame, encode_params)
        if success:
            return encoded.tobytes()
        raise ValueError("Failed to encode frame")
    
    def release(self):
        """Release video capture."""
        if self.cap:
            self.cap.release()
            print("[VideoReader] Released")
    
    def get_metadata(self) -> dict:
        """Get video metadata."""
        return {
            "filepath": self.video_path,
            "filename": os.path.basename(self.video_path),
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration": self.duration
        }
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
