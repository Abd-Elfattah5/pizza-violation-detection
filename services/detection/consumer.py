# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - RabbitMQ Consumer
# ══════════════════════════════════════════════════════════════
#
# Consumes frames from the raw_frames queue published by Frame Reader
#
# ══════════════════════════════════════════════════════════════

import pika
import json
import time
from typing import Callable, Optional
import config


class FrameConsumer:
    """
    Consumes video frames from RabbitMQ.
    
    Usage:
        def process_frame(frame_data: dict):
            # Process the frame
            pass
        
        consumer = FrameConsumer()
        consumer.connect()
        consumer.start_consuming(callback=process_frame)
    """
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.frames_consumed = 0
    
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
                print(f"[Consumer] Connecting to RabbitMQ (attempt {attempt}/{max_retries})...")
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare the queue we'll consume from
                self.channel.queue_declare(
                    queue=config.RAW_FRAMES_QUEUE,
                    durable=True
                )
                
                # Set prefetch count (process one message at a time)
                # This ensures fair distribution if multiple consumers exist
                self.channel.basic_qos(prefetch_count=1)
                
                print(f"[Consumer] ✅ Connected to RabbitMQ!")
                return True
                
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[Consumer] ❌ Connection failed: {e}")
                if attempt < max_retries:
                    print(f"[Consumer] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"[Consumer] ❌ Max retries reached.")
                    return False
        
        return False
    
    def start_consuming(self, callback: Callable[[dict], dict]) -> None:
        """
        Start consuming messages from the queue.
        
        Args:
            callback: Function to process each frame
                      Signature: callback(frame_data: dict) -> dict
                      Returns: processed result dict
        """
        
        if not self.channel:
            print("[Consumer] ❌ Not connected!")
            return
        
        def on_message(ch, method, properties, body):
            """Internal callback wrapper."""
            try:
                # Parse message
                frame_data = json.loads(body.decode('utf-8'))
                
                self.frames_consumed += 1
                frame_num = frame_data.get('frame_number', 'N/A')
                
                if self.frames_consumed % 30 == 0:  # Log every 30 frames
                    print(f"[Consumer] Processing frame {frame_num} (total: {self.frames_consumed})")
                
                # Call the processing callback
                result = callback(frame_data)
                
                # Acknowledge message (remove from queue)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"[Consumer] ❌ Error processing message: {e}")
                # Reject message and requeue it
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Set up consumer
        self.channel.basic_consume(
            queue=config.RAW_FRAMES_QUEUE,
            on_message_callback=on_message,
            auto_ack=False  # Manual acknowledgment
        )
        
        print(f"[Consumer] Waiting for messages on '{config.RAW_FRAMES_QUEUE}'...")
        print(f"[Consumer] Press Ctrl+C to stop")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(f"\n[Consumer] Stopped. Total frames consumed: {self.frames_consumed}")
            self.channel.stop_consuming()
    
    def close(self):
        """Close the connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"[Consumer] Connection closed. Frames consumed: {self.frames_consumed}")
