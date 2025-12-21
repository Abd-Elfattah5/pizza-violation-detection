# ══════════════════════════════════════════════════════════════
# FRAME READER SERVICE - Configuration
# ══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Video Configuration
VIDEO_PATH = os.getenv("VIDEO_PATH", "/videos/sample.mp4")

# Queue Configuration
RAW_FRAMES_QUEUE = "raw_frames"

# Processing Configuration
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "1"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "85"))
TARGET_FPS = float(os.getenv("TARGET_FPS", "0"))


def print_config():
    """Print current configuration"""
    print("=" * 60)
    print("FRAME READER CONFIGURATION")
    print("=" * 60)
    print(f"RABBITMQ_HOST:    {RABBITMQ_HOST}")
    print(f"RABBITMQ_PORT:    {RABBITMQ_PORT}")
    print(f"RABBITMQ_USER:    {RABBITMQ_USER}")
    print(f"VIDEO_PATH:       {VIDEO_PATH}")
    print(f"RAW_FRAMES_QUEUE: {RAW_FRAMES_QUEUE}")
    print(f"FRAME_SKIP:       {FRAME_SKIP}")
    print(f"JPEG_QUALITY:     {JPEG_QUALITY}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
