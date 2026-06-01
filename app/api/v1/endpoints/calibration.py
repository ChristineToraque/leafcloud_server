from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.sensor_calibration import SensorCalibration as SensorCalibrationModel
from app.schemas.calibration import SensorCalibration, SensorCalibrationUpdate

router = APIRouter()

@router.get("/", response_model=List[SensorCalibration])
def get_all_calibrations(db: Session = Depends(get_db)):
    """Retrieve all sensor calibration states."""
    return db.query(SensorCalibrationModel).all()

@router.get("/{calibration_id}", response_model=SensorCalibration)
def get_calibration_by_id(calibration_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific sensor calibration state by ID."""
    calibration = db.query(SensorCalibrationModel).filter(SensorCalibrationModel.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration record not found")
    return calibration

@router.patch("/{calibration_id}", response_model=SensorCalibration)
def update_calibration_state(
    calibration_id: int, 
    update: SensorCalibrationUpdate, 
    db: Session = Depends(get_db)
):
    """Update the is_calibrating state of a sensor."""
    calibration = db.query(SensorCalibrationModel).filter(SensorCalibrationModel.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration record not found")
    
    calibration.is_calibrating = update.is_calibrating
    db.commit()
    db.refresh(calibration)
    return calibration
