# ══════════════════════════════════════════════════════════════
# TEST SCRIPT - Frame Reader Service
# ══════════════════════════════════════════════════════════════

import sys
import os

sys.path.insert(0, 'services/frame_reader')
from video_reader import VideoReader

def test_video_reader():
    """Test video reading capabilities."""
    
    video_dir = "videos"
    video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.mkv', '.avi'))]
    
    if not video_files:
        print("❌ No video files found in videos/")
        return False
    
    print(f"\n{'='*60}")
    print(f"FRAME READER TEST")
    print(f"Found {len(video_files)} video(s): {video_files}")
    print(f"{'='*60}\n")
    
    # Test first video
    video_path = os.path.join(video_dir, video_files[0])
    
    with VideoReader(video_path) as reader:
        # Test 1: Metadata
        print("TEST 1: Video Metadata")
        meta = reader.get_metadata()
        print(f"  ├─ File: {meta['filename']}")
        print(f"  ├─ Size: {meta['width']}x{meta['height']}")
        print(f"  ├─ FPS: {meta['fps']}")
        print(f"  ├─ Frames: {meta['total_frames']}")
        print(f"  └─ Duration: {meta['duration']:.2f}s")
        print("  ✅ PASSED\n")
        
        # Test 2: Read & Encode frames
        print("TEST 2: Read & Encode Frames")
        count = 0
        for frame_num, timestamp, frame in reader.read_frames():
            jpeg = reader.encode_frame(frame)
            print(f"  ├─ Frame {frame_num}: {timestamp:.2f}s | {frame.shape} | JPEG: {len(jpeg):,} bytes")
            count += 1
            if count >= 5:
                print(f"  └─ (stopped after 5 frames)")
                break
        print("  ✅ PASSED\n")
    
    print(f"{'='*60}")
    print("🎉 ALL FRAME READER TESTS PASSED!")
    print(f"{'='*60}\n")
    return True

if __name__ == "__main__":
    success = test_video_reader()
    sys.exit(0 if success else 1)
