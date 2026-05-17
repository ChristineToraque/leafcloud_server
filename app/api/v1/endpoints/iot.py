from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
import shutil
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.tank_config import TankConfig
from app.models.reading import CleanedDailyReading
from app.services.ai_service import process_iot_data_background

router = APIRouter()

@router.post("/upload")
async def upload_iot_data(
    background_tasks: BackgroundTasks,
    tank_id: int = Form(...),
    ph: float = Form(...),
    ec: float = Form(...),
    temp: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint for Raspberry Pi to upload sensor data and images.
    Uses tank_id to link the data dynamically.
    """
    # 1. Verify Tank exists
    tank = db.query(TankConfig).filter(TankConfig.id == tank_id).first()
    if not tank:
        raise HTTPException(status_code=404, detail=f"Tank with ID {tank_id} not found")

    # 2. Prepare Storage Path
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    
    # images/{date}/{tank_name}/
    folder_path = os.path.join(settings.SOURCE_DIR, date_str, tank.tank_name.replace(" ", "_"))
    os.makedirs(folder_path, exist_ok=True)
    
    file_extension = os.path.splitext(image.filename)[1]
    filename = f"reading_{timestamp_str}_{uuid.uuid4().hex[:6]}{file_extension}"
    file_path = os.path.join(folder_path, filename)

    # 3. Save Image to Disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save image: {e}")

    # 4. Create Database Entry (Cleaned Entry with 'is_new_data' flag)
    cleaned_reading = CleanedDailyReading(
        timestamp=now,
        image_path=file_path.replace("\\", "/"),
        ph=ph,
        ec=ec,
        water_temp=temp,
        experiment_id=None,
        is_new_data=True
    )
    db.add(cleaned_reading)
    db.commit()
    db.refresh(cleaned_reading)

    # 5. Trigger Background AI Tasks (Crop + Predict)
    background_tasks.add_task(process_iot_data_background, cleaned_reading.id)

    return {
        "status": "success",
        "message": "Data received and saved",
        "cleaned_id": cleaned_reading.id
    }
