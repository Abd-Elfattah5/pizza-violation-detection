# ══════════════════════════════════════════════════════════════
# DETECTION SERVICE - Database Operations
# ══════════════════════════════════════════════════════════════
#
# Handles PostgreSQL database operations:
# - Saving violations
# - Updating video status
# - Loading ROI configurations
#
# ══════════════════════════════════════════════════════════════

import psycopg2
from psycopg2.extras import RealDictCursor, Json
import time
from typing import Optional, List, Dict
from contextlib import contextmanager
import config


class Database:
    """
    PostgreSQL database handler for the Detection Service.
    """
    
    def __init__(self):
        self.connection = None
    
    def connect(self, max_retries: int = 5, retry_delay: int = 5) -> bool:
        """Connect to PostgreSQL with retry logic."""
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[Database] Connecting to PostgreSQL (attempt {attempt}/{max_retries})...")
                
                self.connection = psycopg2.connect(
                    host=config.POSTGRES_HOST,
                    port=config.POSTGRES_PORT,
                    database=config.POSTGRES_DB,
                    user=config.POSTGRES_USER,
                    password=config.POSTGRES_PASSWORD
                )
                
                # Test connection
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                print(f"[Database] ✅ Connected to PostgreSQL!")
                return True
                
            except psycopg2.Error as e:
                print(f"[Database] ❌ Connection failed: {e}")
                if attempt < max_retries:
                    print(f"[Database] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"[Database] ❌ Max retries reached.")
                    return False
        
        return False
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    # ══════════════════════════════════════════════════════════
    # VIDEO OPERATIONS
    # ══════════════════════════════════════════════════════════
    
    def create_video(self, video_id: str, filename: str, filepath: str,
                     total_frames: int, fps: float, width: int, height: int,
                     duration: float) -> bool:
        """Create a new video record."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO videos (id, filename, filepath, status, total_frames, 
                                       fps, width, height, duration, total_violations)
                    VALUES (%s, %s, %s, 'processing', %s, %s, %s, %s, %s, 0)
                    ON CONFLICT (id) DO UPDATE SET
                        status = 'processing',
                        updated_at = CURRENT_TIMESTAMP
                """, (video_id, filename, filepath, total_frames, fps, width, height, duration))
            return True
        except Exception as e:
            print(f"[Database] ❌ Error creating video: {e}")
            return False
    
    def update_video_progress(self, video_id: str, processed_frames: int) -> bool:
        """Update video processing progress."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE videos 
                    SET processed_frames = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (processed_frames, video_id))
            return True
        except Exception as e:
            print(f"[Database] ❌ Error updating progress: {e}")
            return False
    
    def update_video_completed(self, video_id: str, total_violations: int) -> bool:
        """Mark video as completed."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE videos 
                    SET status = 'completed', 
                        total_violations = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (total_violations, video_id))
            return True
        except Exception as e:
            print(f"[Database] ❌ Error completing video: {e}")
            return False
    
    # ══════════════════════════════════════════════════════════
    # VIOLATION OPERATIONS
    # ══════════════════════════════════════════════════════════
    
    def save_violation(self, video_id: str, frame_number: int, timestamp: float,
                       frame_path: str, bbox_data: dict, description: str) -> bool:
        """Save a violation record."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO violations (video_id, frame_number, timestamp, 
                                           frame_path, bbox_data, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (video_id, frame_number, timestamp, frame_path, 
                      Json(bbox_data), description))
                
                # Update violation count in videos table
                cursor.execute("""
                    UPDATE videos 
                    SET total_violations = total_violations + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (video_id,))
            
            print(f"[Database] ✅ Violation saved: frame {frame_number}")
            return True
        except Exception as e:
            print(f"[Database] ❌ Error saving violation: {e}")
            return False
    
    def get_violations(self, video_id: str) -> List[Dict]:
        """Get all violations for a video."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM violations WHERE video_id = %s
                    ORDER BY frame_number
                """, (video_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"[Database] ❌ Error getting violations: {e}")
            return []
    
    # ══════════════════════════════════════════════════════════
    # ROI OPERATIONS
    # ══════════════════════════════════════════════════════════
    
    def get_active_rois(self) -> List[Dict]:
        """Get all active ROI configurations."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM roi_configs WHERE is_active = true
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"[Database] ❌ Error getting ROIs: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("[Database] Connection closed")
