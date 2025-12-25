# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Configuration
# ══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════
# SERVER CONFIGURATION
# ══════════════════════════════════════════════════════════════

HOST = os.getenv("STREAMING_HOST", "0.0.0.0")
PORT = int(os.getenv("STREAMING_PORT", "8000"))


# ══════════════════════════════════════════════════════════════
# RABBITMQ CONFIGURATION
# ══════════════════════════════════════════════════════════════

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Queue name to consume from
PROCESSED_FRAMES_QUEUE = "processed_frames"


# ══════════════════════════════════════════════════════════════
# POSTGRESQL CONFIGURATION
# ══════════════════════════════════════════════════════════════

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "violations_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")


# ══════════════════════════════════════════════════════════════
# STREAMING CONFIGURATION
# ══════════════════════════════════════════════════════════════

# How often to send frames via WebSocket (in seconds)
STREAM_FRAME_DELAY = float(os.getenv("STREAM_FRAME_DELAY", "0.033"))  # ~30 FPS


def print_config():
    """Print current configuration."""
    print("=" * 60)
    print("STREAMING SERVICE CONFIGURATION")
    print("=" * 60)
    print(f"HOST:              {HOST}")
    print(f"PORT:              {PORT}")
    print(f"RABBITMQ_HOST:     {RABBITMQ_HOST}")
    print(f"RABBITMQ_PORT:     {RABBITMQ_PORT}")
    print(f"POSTGRES_HOST:     {POSTGRES_HOST}")
    print(f"POSTGRES_DB:       {POSTGRES_DB}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
