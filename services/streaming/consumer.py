# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - RabbitMQ Consumer
# ══════════════════════════════════════════════════════════════
#
# Background thread that consumes processed frames from RabbitMQ
# and stores them in the StreamManager for WebSocket clients.
#
# ══════════════════════════════════════════════════════════════

import pika
import json
import base64
import threading
import time
from typing import Optional
import config
from stream_manager import stream_manager, FrameData


class FrameConsumer:
    """
    Background consumer for processed frames.
    
    Runs in a separate thread to not block the FastAPI server.
    """
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._frames_consumed = 0
    
    def connect(self) -> bool:
        """Connect to RabbitMQ."""
        try:
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
            
            print(f"[Consumer] Connecting to RabbitMQ at {config.RABBITMQ_HOST}...")
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(
                queue=config.PROCESSED_FRAMES_QUEUE,
                durable=True
            )
            
            self.channel.basic_qos(prefetch_count=1)
            
            print(f"[Consumer] ✅ Connected to RabbitMQ!")
            return True
            
        except Exception as e:
            print(f"[Consumer] ❌ Connection failed: {e}")
            return False
    
    def _on_message(self, ch, method, properties, body):
        """Handle incoming message."""
        try:
            # Parse message
            message = json.loads(body.decode('utf-8'))
            
            # Extract frame data
            frame_base64 = message.pop("frame_data", "")
            frame_bytes = base64.b64decode(frame_base64) if frame_base64 else b""
            
            # Create FrameData object
            frame_data = FrameData(
                frame_bytes=frame_bytes,
                video_id=message.get("video_id", ""),
                frame_number=message.get("frame_number", 0),
                timestamp=message.get("timestamp", 0.0),
                detections=message.get("detections", []),
                violation_detected=message.get("violation_detected", False),
                violation_count=message.get("violation_count", 0)
            )
            
            # Store in stream manager
            stream_manager.set_frame(frame_data)
            
            self._frames_consumed += 1
            
            # Log every 30 frames
            if self._frames_consumed % 30 == 0:
                print(f"[Consumer] Frames consumed: {self._frames_consumed}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"[Consumer] ❌ Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _consume_loop(self):
        """Main consumption loop (runs in background thread)."""
        while self._running:
            try:
                if not self.connection or self.connection.is_closed:
                    if not self.connect():
                        print("[Consumer] Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                
                # Set up consumer
                self.channel.basic_consume(
                    queue=config.PROCESSED_FRAMES_QUEUE,
                    on_message_callback=self._on_message,
                    auto_ack=False
                )
                
                print(f"[Consumer] Waiting for messages on '{config.PROCESSED_FRAMES_QUEUE}'...")
                
                # Start consuming (blocks until stopped)
                while self._running:
                    self.connection.process_data_events(time_limit=1)
                    
            except Exception as e:
                print(f"[Consumer] ❌ Error in consume loop: {e}")
                if self._running:
                    print("[Consumer] Reconnecting in 5 seconds...")
                    time.sleep(5)
        
        print("[Consumer] Consume loop ended")
    
    def start(self):
        """Start the background consumer thread."""
        if self._thread and self._thread.is_alive():
            print("[Consumer] Already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        print("[Consumer] Background thread started")
    
    def stop(self):
        """Stop the background consumer."""
        print("[Consumer] Stopping...")
        self._running = False
        
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except:
                pass
        
        if self._thread:
            self._thread.join(timeout=5)
        
        print(f"[Consumer] Stopped. Total frames consumed: {self._frames_consumed}")
    
    @property
    def is_running(self) -> bool:
        """Check if consumer is running."""
        return self._running and self._thread and self._thread.is_alive()
    
    @property
    def frames_consumed(self) -> int:
        """Get total frames consumed."""
        return self._frames_consumed


# Global consumer instance
frame_consumer = FrameConsumer()
