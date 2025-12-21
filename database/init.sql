-- ══════════════════════════════════════════════════════════════
-- PIZZA VIOLATION DETECTION - DATABASE SCHEMA
-- ══════════════════════════════════════════════════════════════
--
-- This file runs automatically when PostgreSQL starts for the FIRST time.
-- It creates all the tables we need for our application.
--
-- To re-run this after changes:
--   docker compose down -v   (deletes database volume)
--   docker compose up        (recreates everything)
--
-- ══════════════════════════════════════════════════════════════


-- ══════════════════════════════════════════════════════════════
-- ENABLE UUID EXTENSION
-- ══════════════════════════════════════════════════════════════
-- UUIDs are unique identifiers that look like: 
-- "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
-- Better than auto-increment integers because:
-- 1. Globally unique (can merge databases without ID conflicts)
-- 2. Can't guess the next ID (more secure)
-- 3. Can generate IDs in application code without database
-- ══════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                                -- "IF NOT EXISTS" prevents error if already enabled
                                -- "uuid-ossp" provides uuid_generate_v4() function


-- ══════════════════════════════════════════════════════════════
-- TABLE: videos
-- ══════════════════════════════════════════════════════════════
-- Stores information about each video we process
-- One row per video file
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS videos (
    
    -- Primary Key: Unique identifier for each video
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                -- UUID type: stores unique identifiers
                                -- PRIMARY KEY: must be unique, used to reference this row
                                -- DEFAULT uuid_generate_v4(): auto-generate if not provided
    
    -- Video file information
    filename VARCHAR(255) NOT NULL,
                                -- VARCHAR(255): variable-length string, max 255 characters
                                -- NOT NULL: this field is required, can't be empty
                                -- Example: "Sah w b3dha ghalt.mp4"
    
    filepath VARCHAR(500) NOT NULL,
                                -- Full path to the video file
                                -- Example: "/videos/Sah w b3dha ghalt.mp4"
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'pending',
                                -- DEFAULT 'pending': if not specified, use this value
                                -- Possible values: 'pending', 'processing', 'completed', 'error'
    
    -- Video metadata
    total_frames INTEGER DEFAULT 0,
                                -- INTEGER: whole number
                                -- Total number of frames in the video
    
    processed_frames INTEGER DEFAULT 0,
                                -- How many frames we've processed so far
                                -- Used to show progress percentage
    
    fps FLOAT DEFAULT 0,        -- Frames Per Second
                                -- FLOAT: decimal number
                                -- Example: 30.0, 29.97, 60.0
    
    duration FLOAT DEFAULT 0,   -- Video duration in seconds
                                -- Example: 15.5 (15 and a half seconds)
    
    width INTEGER DEFAULT 0,    -- Video width in pixels
    height INTEGER DEFAULT 0,   -- Video height in pixels
    
    total_violations INTEGER DEFAULT 0,
                                -- Count of violations detected in this video
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                -- TIMESTAMP: date and time
                                -- CURRENT_TIMESTAMP: automatically set to "now"
                                -- When this row was inserted
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                -- When this row was last modified
                                -- We'll update this in our application code
);


-- ══════════════════════════════════════════════════════════════
-- TABLE: violations
-- ══════════════════════════════════════════════════════════════
-- Stores each detected violation
-- One row per violation instance
-- Linked to videos table via video_id (foreign key)
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS violations (
    
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key: Links to the videos table
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
                                -- REFERENCES videos(id): must match an id in videos table
                                -- ON DELETE CASCADE: if video is deleted, delete its violations too
                                -- This maintains data integrity (no orphan violations)
    
    -- Frame information
    frame_number INTEGER NOT NULL,
                                -- Which frame number in the video
                                -- Example: 324 (the 324th frame)
    
    timestamp FLOAT NOT NULL,   -- Time in the video (seconds)
                                -- Example: 10.8 (10.8 seconds into video)
                                -- Calculated: frame_number / fps
    
    -- Saved frame image
    frame_path VARCHAR(500),    -- Path to the saved violation frame image
                                -- Example: "/violations/abc123/frame_324.jpg"
                                -- NULL if we don't save the image
    
    -- Detection data
    bbox_data JSONB,            -- Bounding boxes of objects in the violation
                                -- JSONB: JSON Binary - efficient JSON storage
                                -- Example: {
                                --   "hand": {"x1": 100, "y1": 200, "x2": 150, "y2": 280},
                                --   "pizza": {"x1": 300, "y1": 400, "x2": 500, "y2": 550}
                                -- }
                                -- JSONB allows querying inside the JSON!
    
    description TEXT,           -- Human-readable description
                                -- TEXT: unlimited length string
                                -- Example: "Hand grabbed from protein container without scooper"
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ══════════════════════════════════════════════════════════════
-- TABLE: roi_configs
-- ══════════════════════════════════════════════════════════════
-- Stores Region of Interest configurations
-- ROI = the area we monitor for violations (e.g., protein container)
-- Users can create multiple ROIs and enable/disable them
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS roi_configs (
    
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- ROI identification
    name VARCHAR(100) NOT NULL, -- Human-readable name
                                -- Example: "Protein Container", "Cheese Area"
    
    -- ROI coordinates (rectangle)
    coordinates JSONB NOT NULL, -- Rectangle coordinates as JSON
                                -- Example: {"x1": 100, "y1": 150, "x2": 400, "y2": 400}
                                -- x1,y1 = top-left corner
                                -- x2,y2 = bottom-right corner
    
    -- Display settings
    color VARCHAR(7) DEFAULT '#00FF00',
                                -- Color for drawing ROI on video
                                -- '#00FF00' = bright green (hex color code)
                                -- Format: #RRGGBB
    
    -- Status
    is_active BOOLEAN DEFAULT true,
                                -- BOOLEAN: true or false
                                -- true = this ROI is being monitored
                                -- false = ROI exists but is disabled
                                -- Allows enabling/disabling without deleting
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ══════════════════════════════════════════════════════════════
-- INDEXES
-- ══════════════════════════════════════════════════════════════
-- Indexes speed up queries on specific columns
-- Like an index in a book - helps find things faster
-- Trade-off: uses more storage, slower inserts
-- ══════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_violations_video_id ON violations(video_id);
                                -- Speed up: SELECT * FROM violations WHERE video_id = ?
                                -- Important because we often query violations for a specific video

CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
                                -- Speed up: SELECT * FROM videos WHERE status = 'processing'
                                -- Useful for finding videos in a specific state

CREATE INDEX IF NOT EXISTS idx_roi_active ON roi_configs(is_active);
                                -- Speed up: SELECT * FROM roi_configs WHERE is_active = true
                                -- We query active ROIs frequently during processing


-- ══════════════════════════════════════════════════════════════
-- DEFAULT DATA
-- ══════════════════════════════════════════════════════════════
-- Insert initial data that the application needs
-- ══════════════════════════════════════════════════════════════

INSERT INTO roi_configs (name, coordinates, color, is_active)
VALUES (
    'Protein Container',                            -- name
    '{"x1": 100, "y1": 150, "x2": 400, "y2": 400}', -- coordinates (JSON)
    '#00FF00',                                       -- color (green)
    true                                             -- is_active
)
ON CONFLICT DO NOTHING;         -- If this exact row exists, don't error, just skip
                                -- Prevents duplicate entries if init.sql runs twice
