# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - ROI Configuration Routes
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db

router = APIRouter()


class ROICoordinates(BaseModel):
    """ROI coordinates model."""
    x1: int
    y1: int
    x2: int
    y2: int


class ROICreateRequest(BaseModel):
    """Request to create an ROI."""
    name: str
    coordinates: ROICoordinates
    color: Optional[str] = "#00FF00"


class ROIUpdateRequest(BaseModel):
    """Request to update an ROI."""
    coordinates: Optional[ROICoordinates] = None
    is_active: Optional[bool] = None


@router.get("")
async def get_rois(active_only: bool = True):
    """
    Get ROI configurations.
    
    Args:
        active_only: If True, only return active ROIs
    
    Returns:
        List of ROI configurations
    """
    if active_only:
        rois = db.get_active_rois()
    else:
        rois = db.get_all_rois()
    
    # Convert types
    for roi in rois:
        roi['id'] = str(roi['id'])
        if roi.get('created_at'):
            roi['created_at'] = roi['created_at'].isoformat()
        if roi.get('updated_at'):
            roi['updated_at'] = roi['updated_at'].isoformat()
    
    return {
        "count": len(rois),
        "rois": rois
    }


@router.post("")
async def create_roi(request: ROICreateRequest):
    """
    Create a new ROI configuration.
    
    Args:
        name: Name for the ROI
        coordinates: x1, y1, x2, y2 coordinates
        color: Hex color code for display
    
    Returns:
        Created ROI ID
    """
    coordinates = {
        "x1": request.coordinates.x1,
        "y1": request.coordinates.y1,
        "x2": request.coordinates.x2,
        "y2": request.coordinates.y2
    }
    
    roi_id = db.create_roi(
        name=request.name,
        coordinates=coordinates,
        color=request.color
    )
    
    if roi_id:
        return {
            "message": "ROI created successfully",
            "id": roi_id
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create ROI")


@router.put("/{roi_id}")
async def update_roi(roi_id: str, request: ROIUpdateRequest):
    """
    Update an ROI configuration.
    
    Args:
        roi_id: ID of the ROI to update
        coordinates: New coordinates (optional)
        is_active: New active status (optional)
    
    Returns:
        Success message
    """
    coordinates = None
    if request.coordinates:
        coordinates = {
            "x1": request.coordinates.x1,
            "y1": request.coordinates.y1,
            "x2": request.coordinates.x2,
            "y2": request.coordinates.y2
        }
    
    success = db.update_roi(
        roi_id=roi_id,
        coordinates=coordinates,
        is_active=request.is_active
    )
    
    if success:
        return {"message": "ROI updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update ROI")
