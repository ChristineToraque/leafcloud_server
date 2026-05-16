from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TankConfigBase(BaseModel):
    tank_name: str = Field(..., max_length=50)
    water_volume_liters: float = Field(..., gt=0)
    
    macro_brand_name: Optional[str] = None
    macro_n_pct: float = Field(..., ge=0, le=100)
    macro_p_pct: float = Field(..., ge=0, le=100)
    macro_k_pct: float = Field(..., ge=0, le=100)
    
    micro_brand_name: Optional[str] = None
    micro_n_pct: float = Field(..., ge=0, le=100)
    micro_p_pct: float = Field(..., ge=0, le=100)
    micro_k_pct: float = Field(..., ge=0, le=100)
    
    target_macro_dosage_mll: float = Field(..., ge=0)
    target_micro_dosage_mll: float = Field(..., ge=0)
    
    is_active: bool = True

class TankConfigCreate(TankConfigBase):
    pass

class TankConfigUpdate(BaseModel):
    tank_name: Optional[str] = Field(None, max_length=50)
    water_volume_liters: Optional[float] = Field(None, gt=0)
    macro_brand_name: Optional[str] = None
    macro_n_pct: Optional[float] = Field(None, ge=0, le=100)
    macro_p_pct: Optional[float] = Field(None, ge=0, le=100)
    macro_k_pct: Optional[float] = Field(None, ge=0, le=100)
    micro_brand_name: Optional[str] = None
    micro_n_pct: Optional[float] = Field(None, ge=0, le=100)
    micro_p_pct: Optional[float] = Field(None, ge=0, le=100)
    micro_k_pct: Optional[float] = Field(None, ge=0, le=100)
    target_macro_dosage_mll: Optional[float] = Field(None, ge=0)
    target_micro_dosage_mll: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class TankConfigResponse(TankConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
