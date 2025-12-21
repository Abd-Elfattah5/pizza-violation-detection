# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - Configuration
# ══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════
# RABBITMQ CONFIGURATION
# ══════════════════════════════════════════════════════════════

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Queue names
RAW_FRAMES_QUEUE = "raw_frames"             # Input: frames from Frame Reader
PROCESSED_FRAMES_QUEUE = "processed_frames" # Output: frames with detections


# ══════════════════════════════════════════════════════════════
# POSTGRESQL CONFIGURATION
# ══════════════════════════════════════════════════════════════

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "violations_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")


# ══════════════════════════════════════════════════════════════
# MODEL CONFIGURATION
# ══════════════════════════════════════════════════════════════

MODEL_PATH = os.getenv("MODEL_PATH", "models/yolo_model.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))


# ══════════════════════════════════════════════════════════════
# ROI CONFIGURATION (Default - can be overridden from database)
# ══════════════════════════════════════════════════════════════

DEFAULT_ROI = {
    "x1": int(os.getenv("ROI_X1", "100")),
    "y1": int(os.getenv("ROI_Y1", "150")),
    "x2": int(os.getenv("ROI_X2", "400")),
    "y2": int(os.getenv("ROI_Y2", "400"))
}


# ══════════════════════════════════════════════════════════════
# VIOLATION TRACKING CONFIGURATION
# ══════════════════════════════════════════════════════════════

# How many frames to track a hand after it leaves ROI
FRAMES_TO_TRACK_AFTER_ROI = int(os.getenv("FRAMES_TO_TRACK_AFTER_ROI", "90"))

# Margin (pixels) for determining if objects are "near" each other
PROXIMITY_MARGIN = int(os.getenv("PROXIMITY_MARGIN", "50"))


# ══════════════════════════════════════════════════════════════
# OUTPUT CONFIGURATION
# ══════════════════════════════════════════════════════════════

VIOLATIONS_DIR = os.getenv("VIOLATIONS_DIR", "/violations")
SAVE_VIOLATION_FRAMES = os.getenv("SAVE_VIOLATION_FRAMES", "true").lower() == "true"


def print_config():
    """Print current configuration."""
    print("=" * 60)
    print("DETECTION SERVICE CONFIGURATION")
    print("=" * 60)
    print(f"RABBITMQ_HOST:       {RABBITMQ_HOST}")
    print(f"RABBITMQ_PORT:       {RABBITMQ_PORT}")
    print(f"POSTGRES_HOST:       {POSTGRES_HOST}")
    print(f"POSTGRES_DB:         {POSTGRES_DB}")
    print(f"MODEL_PATH:          {MODEL_PATH}")
    print(f"CONFIDENCE:          {CONFIDENCE_THRESHOLD}")
    print(f"DEFAULT_ROI:         {DEFAULT_ROI}")
    print(f"VIOLATIONS_DIR:      {VIOLATIONS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
