# ══════════════════════════════════════════════════════════════
# FRAME READER SERVICE - Main Entry Point
# ══════════════════════════════════════════════════════════════

import sys
import time
import uuid
import os

import config
from video_reader import VideoReader
from publisher import FramePublisher


def generate_video_id() -> str:
    """Generate unique ID for video processing session."""
    return str(uuid.uuid4())


def process_video(video_path: str) -> dict:
    """Process video: read frames and publish to RabbitMQ."""
    video_id = generate_video_id()
    print(f"\n{'='*60}")
    print(f"STARTING VIDEO PROCESSING")
    print(f"Video ID: {video_id}")
    print(f"Path: {video_path}")
    print(f"{'='*60}\n")
    
    frames_processed = 0
    start_time = time.time()
    
    with VideoReader(video_path) as reader, FramePublisher() as publisher:
        video_metadata = reader.get_metadata()
        
        for frame_number, timestamp, frame in reader.read_frames():
            frame_bytes = reader.encode_frame(frame)
            
            frame_metadata = {
                "video_id": video_id,
                "frame_number": frame_number,
                "timestamp": timestamp,
                "width": reader.width,
                "height": reader.height,
                "fps": reader.fps,
                "total_frames": reader.total_frames,
                "filename": video_metadata["filename"]
            }
            
            if publisher.publish_frame(frame_bytes, frame_metadata):
                frames_processed += 1
            
            if config.TARGET_FPS > 0:
                time.sleep(1.0 / config.TARGET_FPS)
    
    duration = time.time() - start_time
    stats = {
        "video_id": video_id,
        "frames_processed": frames_processed,
        "duration": duration,
        "fps": frames_processed / duration if duration > 0 else 0,
        "success": frames_processed > 0
    }
    
    print(f"\n{'='*60}")
    print(f"COMPLETE: {frames_processed} frames in {duration:.2f}s")
    print(f"{'='*60}\n")
    
    return stats


def main():
    """Main entry point."""
    config.print_config()
    
    video_path = sys.argv[1] if len(sys.argv) > 1 else config.VIDEO_PATH
    
    if not os.path.exists(video_path):
        print(f"[Main] ❌ Video not found: {video_path}")
        sys.exit(1)
    
    try:
        stats = process_video(video_path)
        sys.exit(0 if stats["success"] else 1)
    except KeyboardInterrupt:
        print("\n[Main] Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"[Main] ❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
