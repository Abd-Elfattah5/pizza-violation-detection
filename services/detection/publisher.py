# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - RabbitMQ Publisher
# ══════════════════════════════════════════════════════════════
#
# Publishes processed frames to the processed_frames queue
# for the Streaming Service to consume
#
# ══════════════════════════════════════════════════════════════

import pika
import json
import time
import base64
from typing import Optional
import config


class ProcessedFramePublisher:
    """
    Publishes processed frames (with detections) to RabbitMQ.
    """
    
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
                
                # Declare the output queue
                self.channel.queue_declare(
                    queue=config.PROCESSED_FRAMES_QUEUE,
                    durable=True
                )
                
                print(f"[Publisher] ✅ Connected! Queue: {config.PROCESSED_FRAMES_QUEUE}")
                return True
                
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[Publisher] ❌ Connection failed: {e}")
                if attempt < max_retries:
                    print(f"[Publisher] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def publish_processed_frame(self, frame_bytes: bytes, metadata: dict) -> bool:
        """
        Publish a processed frame with detection results.
        
        Args:
            frame_bytes: JPEG-encoded frame with bounding boxes drawn
            metadata: Detection metadata including:
                - video_id
                - frame_number
                - timestamp
                - detections: list of detected objects
                - violation_detected: bool
                - violation_count: int
        
        Returns:
            True if published successfully
        """
        
        if not self.channel:
            print("[Publisher] ❌ Not connected!")
            return False
        
        try:
            # Encode frame to base64
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            # Create message
            message = {
                **metadata,
                "frame_data": frame_base64
            }
            
            message_body = json.dumps(message).encode('utf-8')
            
            # Publish
            self.channel.basic_publish(
                exchange='',
                routing_key=config.PROCESSED_FRAMES_QUEUE,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
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
