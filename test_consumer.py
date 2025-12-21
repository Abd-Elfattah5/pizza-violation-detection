# ══════════════════════════════════════════════════════════════
# TEST SCRIPT - Consume Frames from RabbitMQ
# ══════════════════════════════════════════════════════════════

import sys
import json
import base64
import pika

sys.path.insert(0, 'services/frame_reader')
import config

config.RABBITMQ_HOST = "localhost"


def test_consumer():
    """Test consuming frames from RabbitMQ."""
    
    print(f"\n{'='*60}")
    print("FRAME CONSUMER TEST")
    print(f"{'='*60}")
    print(f"RabbitMQ: {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
    print(f"Queue: {config.RAW_FRAMES_QUEUE}")
    print(f"{'='*60}\n")
    
    # Connect
    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    
    # Check queue
    queue = channel.queue_declare(queue=config.RAW_FRAMES_QUEUE, durable=True, passive=True)
    message_count = queue.method.message_count
    print(f"Messages in queue: {message_count}\n")
    
    if message_count == 0:
        print("❌ No messages to consume")
        print("   Run test_publishing.py first")
        connection.close()
        return False
    
    # Consume a few messages
    print("Consuming messages:")
    print("-" * 40)
    
    consumed = 0
    max_consume = 5
    
    for method, properties, body in channel.consume(queue=config.RAW_FRAMES_QUEUE, inactivity_timeout=1):
        if method is None:
            break
        
        # Parse message
        message = json.loads(body.decode('utf-8'))
        
        # Extract info (don't decode full frame, just check size)
        frame_data = message.pop('frame_data')
        frame_size = len(base64.b64decode(frame_data))
        
        print(f"  Message {consumed + 1}:")
        print(f"    ├─ video_id: {message.get('video_id', 'N/A')}")
        print(f"    ├─ frame_number: {message.get('frame_number', 'N/A')}")
        print(f"    ├─ timestamp: {message.get('timestamp', 'N/A'):.2f}s")
        print(f"    ├─ dimensions: {message.get('width', 'N/A')}x{message.get('height', 'N/A')}")
        print(f"    └─ frame_size: {frame_size:,} bytes")
        
        # Acknowledge message (remove from queue)
        channel.basic_ack(method.delivery_tag)
        
        consumed += 1
        if consumed >= max_consume:
            print(f"\n  (stopped after {consumed} messages)")
            break
    
    # Cancel consumer
    channel.cancel()
    connection.close()
    
    print("-" * 40)
    print(f"\n✅ Successfully consumed {consumed} messages")
    
    print(f"\n{'='*60}")
    print("🎉 CONSUMER TEST PASSED!")
    print(f"{'='*60}\n")
    
    return True


if __name__ == "__main__":
    success = test_consumer()
    sys.exit(0 if success else 1)
