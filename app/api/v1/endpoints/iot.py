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
from app.models.npk_prediction import NPKPrediction
from app.schemas.dashboard import DashboardResponse, TelemetryData, NutrientEstimation, ActionableAlert

router = APIRouter()

@router.get("/dashboard/{tank_id}", response_model=DashboardResponse)
def get_tank_dashboard(tank_id: int, db: Session = Depends(get_db)):
    """
    Returns the real-time monitoring dashboard data for a specific tank.
    Performs the dynamic math to convert AI scales into physical grams and alerts.
    """
    # 1. Fetch Config
    tank = db.query(TankConfig).filter(TankConfig.id == tank_id).first()
    if not tank:
        raise HTTPException(status_code=404, detail="Tank configuration not found")

    # 2. Fetch Latest Reading
    latest_reading = db.query(CleanedDailyReading).filter(
        CleanedDailyReading.tank_id == tank_id
    ).order_by(CleanedDailyReading.timestamp.desc()).first()

    if not latest_reading:
        raise HTTPException(status_code=404, detail="No readings found for this tank")

    # 3. Fetch AI Prediction for that reading
    prediction = db.query(NPKPrediction).filter(
        NPKPrediction.daily_reading_id == latest_reading.id
    ).first()

    # Default scales if AI hasn't run yet
    macro_scale = prediction.macro_scale if prediction and prediction.macro_scale is not None else 1.0
    micro_scale = prediction.micro_scale if prediction and prediction.micro_scale is not None else 1.0

    # 4. PERFORM DYNAMIC MATH
    # Grams = (Scaling Index * Target Dosage mL/L * Tank Volume L) * (NPK % / 100)
    
    # Calculate Macro Contribution
    macro_weight_total = tank.target_macro_dosage_mll * tank.water_volume_liters
    n_from_macro = (macro_scale * macro_weight_total) * (tank.macro_n_pct / 100)
    p_from_macro = (macro_scale * macro_weight_total) * (tank.macro_p_pct / 100)
    k_from_macro = (macro_scale * macro_weight_total) * (tank.macro_k_pct / 100)

    # Calculate Micro Contribution
    micro_weight_total = tank.target_micro_dosage_mll * tank.water_volume_liters
    n_from_micro = (micro_scale * micro_weight_total) * (tank.micro_n_pct / 100)
    p_from_micro = (micro_scale * micro_weight_total) * (tank.micro_p_pct / 100)
    k_from_micro = (micro_scale * micro_weight_total) * (tank.micro_k_pct / 100)

    # 5. Determine Profile Status
    profile = "Balanced"
    if macro_scale > micro_scale + 0.3:
        profile = "Macro-Leaning Blend"
    elif micro_scale > macro_scale + 0.3:
        profile = "Micro-Leaning Blend"
    
    # 6. Generate Actionable Alert
    alert = None
    if macro_scale < 0.7 or micro_scale < 0.7:
        topup_macro = max(0, (1.0 - macro_scale) * tank.target_macro_dosage_mll * tank.water_volume_liters)
        topup_micro = max(0, (1.0 - micro_scale) * tank.target_micro_dosage_mll * tank.water_volume_liters)
        
        alert = ActionableAlert(
            level="WARNING",
            message=f"Nutrient levels have dropped to {int(min(macro_scale, micro_scale)*100)}% of recommended dosage.",
            action_required=True,
            topup_macro_ml=round(topup_macro, 1),
            topup_micro_ml=round(topup_micro, 1)
        )

    # 7. Construct Response
    return DashboardResponse(
        tank_id=tank.id,
        tank_name=tank.tank_name,
        last_updated=latest_reading.timestamp,
        image_url=latest_reading.image_path,
        health_status="HEALTHY" if macro_scale > 0.8 else "NUTRIENT DEFICIENT",
        profile_detected=profile,
        telemetry=TelemetryData(
            ph=latest_reading.ph,
            ec=latest_reading.ec,
            water_temp=latest_reading.water_temp,
            status="Safe Range" if 5.5 <= latest_reading.ph <= 6.5 else "Action Needed"
        ),
        estimated_nutrients=NutrientEstimation(
            n_grams=round(n_from_macro + n_from_micro, 2),
            p_grams=round(p_from_macro + p_from_micro, 2),
            k_grams=round(k_from_macro + k_from_micro, 2)
        ),
        alert=alert
    )

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
        tank_id=tank_id,
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
