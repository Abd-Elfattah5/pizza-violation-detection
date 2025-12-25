# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Database Operations
# ══════════════════════════════════════════════════════════════
#
# Read-only database operations for the Streaming Service
#
# ══════════════════════════════════════════════════════════════

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Dict, Optional
from contextlib import contextmanager
import config


class Database:
    """PostgreSQL database handler for Streaming Service."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def connect(self) -> bool:
        """Connect to PostgreSQL."""
        try:
            print(f"[Database] Connecting to PostgreSQL...")
            self.connection = psycopg2.connect(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                database=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD
            )
            print(f"[Database] ✅ Connected!")
            return True
        except psycopg2.Error as e:
            print(f"[Database] ❌ Connection failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self.connection is not None and self.connection.closed == 0
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        if not self.is_connected():
            self.connect()
        
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
    
    def get_all_videos(self) -> List[Dict]:
        """Get all videos."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, filename, filepath, status, total_frames, 
                           processed_frames, fps, duration, width, height,
                           total_violations, created_at, updated_at
                    FROM videos
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Database] ❌ Error getting videos: {e}")
            return []
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """Get a specific video by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM videos WHERE id = %s
                """, (video_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"[Database] ❌ Error getting video: {e}")
            return None
    
    def get_video_by_status(self, status: str) -> List[Dict]:
        """Get videos by status."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM videos WHERE status = %s
                    ORDER BY created_at DESC
                """, (status,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Database] ❌ Error getting videos by status: {e}")
            return []
    
    # ══════════════════════════════════════════════════════════
    # VIOLATION OPERATIONS
    # ══════════════════════════════════════════════════════════
    
    def get_violations(self, video_id: str = None) -> List[Dict]:
        """Get violations, optionally filtered by video_id."""
        try:
            with self.get_cursor() as cursor:
                if video_id:
                    cursor.execute("""
                        SELECT * FROM violations 
                        WHERE video_id = %s
                        ORDER BY frame_number
                    """, (video_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM violations
                        ORDER BY created_at DESC
                        LIMIT 100
                    """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Database] ❌ Error getting violations: {e}")
            return []
    
    def get_violation_count(self, video_id: str = None) -> int:
        """Get total violation count."""
        try:
            with self.get_cursor() as cursor:
                if video_id:
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM violations WHERE video_id = %s
                    """, (video_id,))
                else:
                    cursor.execute("SELECT COUNT(*) as count FROM violations")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"[Database] ❌ Error getting violation count: {e}")
            return 0
    
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
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Database] ❌ Error getting ROIs: {e}")
            return []
    
    def get_all_rois(self) -> List[Dict]:
        """Get all ROI configurations."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM roi_configs ORDER BY created_at")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Database] ❌ Error getting ROIs: {e}")
            return []
    
    def create_roi(self, name: str, coordinates: dict, color: str = "#00FF00") -> Optional[str]:
        """Create a new ROI configuration."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO roi_configs (name, coordinates, color, is_active)
                    VALUES (%s, %s, %s, true)
                    RETURNING id
                """, (name, Json(coordinates), color))
                result = cursor.fetchone()
                return str(result['id']) if result else None
        except Exception as e:
            print(f"[Database] ❌ Error creating ROI: {e}")
            return None
    
    def update_roi(self, roi_id: str, coordinates: dict = None, 
                   is_active: bool = None) -> bool:
        """Update an ROI configuration."""
        try:
            with self.get_cursor() as cursor:
                if coordinates is not None:
                    cursor.execute("""
                        UPDATE roi_configs 
                        SET coordinates = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (Json(coordinates), roi_id))
                
                if is_active is not None:
                    cursor.execute("""
                        UPDATE roi_configs 
                        SET is_active = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (is_active, roi_id))
                
                return True
        except Exception as e:
            print(f"[Database] ❌ Error updating ROI: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("[Database] Connection closed")


# Global database instance
db = Database()
