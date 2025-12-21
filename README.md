# 🍕 Pizza Store Violation Detection System

A microservices-based computer vision system for monitoring hygiene protocol compliance in pizza stores.

## 🎯 Overview

This system automatically detects whether workers are using a **scooper** when picking up ingredients (like proteins) from designated areas. Any action of grabbing ingredients **without a scooper** and placing them on a pizza is flagged as a **violation**.

### Key Features

- ✅ Real-time video processing with YOLO object detection
- ✅ Tracks hands, scoopers, and pizzas
- ✅ State machine-based violation detection logic
- ✅ WebSocket streaming to frontend
- ✅ Database storage of violations
- ✅ Configurable Regions of Interest (ROI)
- ✅ Handles multiple workers simultaneously
- ✅ Distinguishes between cleaning and grabbing actions

---

## 🏗️ Architecture

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│ Frame Reader │────►│  RabbitMQ   │────►│  Detection   │────►│  Streaming  │────►│ Frontend │
│   Service    │     │   Broker    │     │   Service    │     │   Service   │     │    UI    │
└──────────────┘     └─────────────┘     └──────┬───────┘     └─────────────┘     └──────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │ PostgreSQL  │
                                         │  Database   │
                                         └─────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 80 | Web UI for monitoring |
| **Streaming** | 8000 | REST API & WebSocket server |
| **Frame Reader** | - | Reads video frames |
| **Detection** | - | YOLO detection & violation logic |
| **RabbitMQ** | 5672, 15672 | Message broker |
| **PostgreSQL** | 5432 | Database |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with drivers (for fast processing)
- ~4GB disk space

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd pizza-violation-detection

# 2. Download the YOLO model
# Place yolo_model.pt in: services/detection/models/

# 3. Add test videos
# Place .mp4 files in: videos/

# 4. Start all services
docker compose up --build

# 5. Open the UI
# Navigate to: http://localhost
```

### Stopping

```bash
# Stop all services (keep data)
docker compose down

# Stop and delete all data
docker compose down -v
```

---

## 📦 Project Structure

```
pizza-violation-detection/
├── docker-compose.yml          # Service orchestration
├── .env                        # Environment variables
├── database/
│   └── init.sql               # Database schema
├── services/
│   ├── frame_reader/          # Video reading service
│   ├── detection/             # YOLO + violation logic
│   ├── streaming/             # FastAPI backend
│   └── frontend/              # Web UI
├── videos/                    # Input videos
└── violations/                # Saved violation frames
```

---

## 🔌 API Endpoints

### REST API (http://localhost:8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/videos` | List all videos |
| POST | `/api/videos/start` | Start processing |
| GET | `/api/violations` | Get violations |
| GET | `/api/roi` | Get ROI configs |
| POST | `/api/roi` | Create/update ROI |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws/video-stream` | Real-time video stream |

### API Documentation

FastAPI auto-generates documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧠 Violation Detection Logic

### State Machine

Each tracked hand goes through states:

```
IDLE → IN_ROI → LEFT_ROI → [Check destination]
                              │
                              ├─► Pizza + No Scooper = ❌ VIOLATION
                              ├─► Pizza + Scooper = ✅ OK
                              └─► Not Pizza = ✅ OK (cleaning)
```

### What Counts as a Violation?

| Scenario | Result |
|----------|--------|
| Hand grabs from ROI → goes to pizza → NO scooper | ❌ **VIOLATION** |
| Hand grabs from ROI → goes to pizza → WITH scooper | ✅ OK |
| Hand enters ROI → leaves → doesn't go to pizza | ✅ OK (cleaning) |
| Hand goes directly to pizza (no ROI visit) | ✅ OK |

---

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all available options.

### ROI Configuration

ROIs can be configured via:
1. Environment variables (default ROI)
2. Database (via API)
3. Frontend UI

---

## 🧪 Testing

### Test Videos

| Video | Expected Violations |
|-------|---------------------|
| Sah w b3dha ghalt.mp4 | 1 |
| Sah w b3dha ghalt (2).mp4 | 2 |
| Sah w b3dha ghalt (3).mp4 | 1 |

### Verify System

```bash
# Check all services are running
docker compose ps

# View logs
docker compose logs -f

# Access RabbitMQ management
open http://localhost:15672   # guest/guest
```

---

## 📝 License

MIT

---

## 👤 Author

Abdelfattah Mohammed

---

