from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TelemetryData(BaseModel):
    ph: float
    ec: float
    water_temp: float
    status: str

class NutrientEstimation(BaseModel):
    n_grams: float
    p_grams: float
    k_grams: float
    unit: str = "grams"

class ActionableAlert(BaseModel):
    level: str # INFO, WARNING, CRITICAL
    message: str
    action_required: bool
    topup_macro_ml: float
    topup_micro_ml: float

class DashboardResponse(BaseModel):
    tank_id: int
    tank_name: str
    last_updated: datetime
    image_url: str
    health_status: str # e.g., HEALTHY, NUTRIENT DEFICIENT
    profile_detected: str # e.g., Macro-Leaning Blend
    
    telemetry: TelemetryData
    estimated_nutrients: NutrientEstimation
    alert: Optional[ActionableAlert] = None
