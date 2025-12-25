# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Stream Manager
# ══════════════════════════════════════════════════════════════
#
# Thread-safe manager for the latest video frame.
# Allows the RabbitMQ consumer to store frames and
# WebSocket clients to read them.
#
# ══════════════════════════════════════════════════════════════

import threading
from typing import Optional, Dict, List
from dataclasses import dataclass, field
import time


@dataclass
class FrameData:
    """Container for frame data and metadata."""
    frame_bytes: bytes                      # JPEG encoded frame
    video_id: str = ""
    frame_number: int = 0
    timestamp: float = 0.0
    detections: List[Dict] = field(default_factory=list)
    violation_detected: bool = False
    violation_count: int = 0
    received_at: float = field(default_factory=time.time)


class StreamManager:
    """
    Thread-safe manager for video stream data.
    
    Singleton pattern - only one instance exists.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the stream manager."""
        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[FrameData] = None
        self._frame_count = 0
        self._connected_clients = 0
        self._is_streaming = False
        self._current_video_id: Optional[str] = None
        
        print("[StreamManager] Initialized")
    
    def set_frame(self, frame_data: FrameData):
        """
        Store the latest frame (called by consumer).
        
        Thread-safe: Uses lock to prevent race conditions.
        """
        with self._frame_lock:
            self._latest_frame = frame_data
            self._frame_count += 1
            self._is_streaming = True
            self._current_video_id = frame_data.video_id
    
    def get_frame(self) -> Optional[FrameData]:
        """
        Get the latest frame (called by WebSocket).
        
        Thread-safe: Uses lock to prevent race conditions.
        """
        with self._frame_lock:
            return self._latest_frame
    
    def clear_frame(self):
        """Clear the current frame."""
        with self._frame_lock:
            self._latest_frame = None
            self._is_streaming = False
    
    @property
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._is_streaming
    
    @property
    def current_video_id(self) -> Optional[str]:
        """Get current video ID being streamed."""
        return self._current_video_id
    
    @property
    def frame_count(self) -> int:
        """Get total frames received."""
        return self._frame_count
    
    def add_client(self):
        """Register a new WebSocket client."""
        with self._frame_lock:
            self._connected_clients += 1
            print(f"[StreamManager] Client connected. Total: {self._connected_clients}")
    
    def remove_client(self):
        """Unregister a WebSocket client."""
        with self._frame_lock:
            self._connected_clients = max(0, self._connected_clients - 1)
            print(f"[StreamManager] Client disconnected. Total: {self._connected_clients}")
    
    @property
    def connected_clients(self) -> int:
        """Get number of connected clients."""
        return self._connected_clients
    
    def get_status(self) -> Dict:
        """Get current stream status."""
        return {
            "is_streaming": self._is_streaming,
            "current_video_id": self._current_video_id,
            "frame_count": self._frame_count,
            "connected_clients": self._connected_clients,
            "has_frame": self._latest_frame is not None
        }


# Global stream manager instance
stream_manager = StreamManager()
