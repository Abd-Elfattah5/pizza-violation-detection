# ══════════════════════════════════════════════════════════════
# TEST SCRIPT - Frame Reader Publishing to RabbitMQ
# ══════════════════════════════════════════════════════════════

import sys
import os
import time

sys.path.insert(0, 'services/frame_reader')

from video_reader import VideoReader
from publisher import FramePublisher
import config

# Override config for local testing
config.RABBITMQ_HOST = "localhost"  # Connect to Docker from host machine


def test_publishing():
    """Test publishing frames to RabbitMQ."""
    
    video_dir = "videos"
    video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.mkv'))]
    
    if not video_files:
        print("❌ No videos found")
        return False
    
    video_path = os.path.join(video_dir, video_files[0])
    
    print(f"\n{'='*60}")
    print("FRAME PUBLISHING TEST")
    print(f"{'='*60}")
    print(f"Video: {video_path}")
    print(f"RabbitMQ: {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
    print(f"Queue: {config.RAW_FRAMES_QUEUE}")
    print(f"{'='*60}\n")
    
    # Test 1: Connect to RabbitMQ
    print("TEST 1: Connect to RabbitMQ")
    publisher = FramePublisher()
    
    if not publisher.connect(max_retries=3, retry_delay=2):
        print("❌ Could not connect to RabbitMQ")
        print("   Make sure RabbitMQ is running: docker compose up -d rabbitmq")
        return False
    print("✅ Connected to RabbitMQ\n")
    
    # Test 2: Publish frames
    print("TEST 2: Publish Frames")
    
    with VideoReader(video_path) as reader:
        metadata = reader.get_metadata()
        frames_published = 0
        
        for frame_num, timestamp, frame in reader.read_frames():
            # Encode frame
            frame_bytes = reader.encode_frame(frame)
            
            # Create metadata
            frame_metadata = {
                "video_id": "test-video-123",
                "frame_number": frame_num,
                "timestamp": timestamp,
                "width": reader.width,
                "height": reader.height,
                "fps": reader.fps,
                "total_frames": reader.total_frames,
                "filename": metadata["filename"]
            }
            
            # Publish
            if publisher.publish_frame(frame_bytes, frame_metadata):
                frames_published += 1
                print(f"  ├─ Published frame {frame_num} ({len(frame_bytes):,} bytes)")
            else:
                print(f"  ├─ ❌ Failed to publish frame {frame_num}")
            
            # Only publish 10 frames for testing
            if frames_published >= 10:
                print(f"  └─ (stopped after {frames_published} frames)")
                break
    
    publisher.close()
    
    print(f"\n✅ Published {frames_published} frames to RabbitMQ\n")
    
    # Test 3: Verify messages in queue
    print("TEST 3: Verify Messages in Queue")
    print("   Checking queue status...")
    
    import pika
    
    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    
    # Get queue info
    queue = channel.queue_declare(queue=config.RAW_FRAMES_QUEUE, durable=True, passive=True)
    message_count = queue.method.message_count
    
    print(f"   Queue '{config.RAW_FRAMES_QUEUE}' has {message_count} messages")
    connection.close()
    
    if message_count >= frames_published:
        print("✅ All messages are in the queue!\n")
    else:
        print("⚠️ Some messages might be missing\n")
    
    print(f"{'='*60}")
    print("🎉 PUBLISHING TEST PASSED!")
    print(f"{'='*60}")
    print(f"\nYou can also check RabbitMQ Management UI:")
    print(f"   URL: http://localhost:15672")
    print(f"   Login: guest / guest")
    print(f"   Go to 'Queues' tab to see '{config.RAW_FRAMES_QUEUE}'\n")
    
    return True


if __name__ == "__main__":
    success = test_publishing()
    sys.exit(0 if success else 1)
