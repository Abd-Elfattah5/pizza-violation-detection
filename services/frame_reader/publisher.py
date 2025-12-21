# ══════════════════════════════════════════════════════════════
# FRAME READER SERVICE - RabbitMQ Publisher
# ══════════════════════════════════════════════════════════════

import pika
import json
import time
import base64
from typing import Optional
import config


class FramePublisher:
    """Publishes video frames to RabbitMQ."""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.frames_published = 0
    
    def connect(self, max_retries: int = 5, retry_delay: int = 5) -> bool:
        """Connect to RabbitMQ with retry logic."""
        credentials = pika.PlainCredentials(
            config.RABBITMQ_USER,
            config.RABBITMQ_PASS
        )
        
        parameters = pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[Publisher] Connecting to RabbitMQ (attempt {attempt}/{max_retries})...")
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=config.RAW_FRAMES_QUEUE, durable=True)
                print(f"[Publisher] ✅ Connected to RabbitMQ!")
                return True
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[Publisher] ❌ Connection failed: {e}")
                if attempt < max_retries:
                    print(f"[Publisher] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"[Publisher] ❌ Max retries reached.")
                    return False
        return False
    
    def publish_frame(self, frame_bytes: bytes, metadata: dict) -> bool:
        """Publish a single frame to RabbitMQ."""
        if not self.channel:
            print("[Publisher] ❌ Not connected!")
            return False
        
        try:
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            message = {**metadata, "frame_data": frame_base64}
            message_body = json.dumps(message).encode('utf-8')
            
            self.channel.basic_publish(
                exchange='',
                routing_key=config.RAW_FRAMES_QUEUE,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            self.frames_published += 1
            return True
        except Exception as e:
            print(f"[Publisher] ❌ Failed to publish: {e}")
            return False
    
    def close(self):
        """Close the connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"[Publisher] Closed. Frames published: {self.frames_published}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
