# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - WebSocket Route
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import base64
import json
import config
from stream_manager import stream_manager

router = APIRouter()


@router.websocket("/ws/video-stream")
async def video_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time video streaming.
    
    Sends frames as JSON:
    {
        "type": "frame",
        "video_id": "...",
        "frame_number": 42,
        "timestamp": 1.4,
        "frame_data": "<base64 JPEG>",
        "detections": [...],
        "violation_detected": false,
        "violation_count": 0
    }
    """
    await websocket.accept()
    stream_manager.add_client()
    
    print(f"[WebSocket] Client connected")
    
    last_frame_number = -1
    
    try:
        while True:
            # Get latest frame
            frame_data = stream_manager.get_frame()
            
            if frame_data and frame_data.frame_number != last_frame_number:
                # New frame available - send it
                message = {
                    "type": "frame",
                    "video_id": frame_data.video_id,
                    "frame_number": frame_data.frame_number,
                    "timestamp": frame_data.timestamp,
                    "frame_data": base64.b64encode(frame_data.frame_bytes).decode('utf-8'),
                    "detections": frame_data.detections,
                    "violation_detected": frame_data.violation_detected,
                    "violation_count": frame_data.violation_count
                }
                
                await websocket.send_json(message)
                last_frame_number = frame_data.frame_number
            
            else:
                # No new frame - send status update
                status = {
                    "type": "status",
                    "is_streaming": stream_manager.is_streaming,
                    "frame_count": stream_manager.frame_count,
                    "connected_clients": stream_manager.connected_clients
                }
                await websocket.send_json(status)
            
            # Control frame rate
            await asyncio.sleep(config.STREAM_FRAME_DELAY)
            
    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        stream_manager.remove_client()
