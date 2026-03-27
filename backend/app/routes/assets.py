from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services.asset_service import AssetService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new asset"""
    asset = AssetService.create_asset(db, current_user.id, asset_data)
    return asset


@router.get("", response_model=List[AssetResponse])
def get_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets for current user"""
    assets = AssetService.get_assets(db, current_user.id)
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific asset"""
    asset = AssetService.get_asset(db, asset_id, current_user.id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an asset"""
    asset = AssetService.update_asset(db, asset_id, current_user.id, asset_data)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an asset"""
    success = AssetService.delete_asset(db, asset_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return None
