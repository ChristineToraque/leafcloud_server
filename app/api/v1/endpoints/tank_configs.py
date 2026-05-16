from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.tank_config import TankConfig
from app.schemas.tank_config import TankConfigCreate, TankConfigUpdate, TankConfigResponse

router = APIRouter()

@router.post("/", response_model=TankConfigResponse, status_code=status.HTTP_201_CREATED)
def create_tank_config(config: TankConfigCreate, db: Session = Depends(get_db)):
    """Creates a new tank configuration."""
    new_config = TankConfig(**config.model_dump())
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config

@router.get("/", response_model=List[TankConfigResponse])
def list_tank_configs(db: Session = Depends(get_db)):
    """Lists all tank configurations."""
    return db.query(TankConfig).all()

@router.get("/{config_id}", response_model=TankConfigResponse)
def get_tank_config(config_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific tank configuration by ID."""
    config = db.query(TankConfig).filter(TankConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.patch("/{config_id}", response_model=TankConfigResponse)
def update_tank_config(config_id: int, update_data: TankConfigUpdate, db: Session = Depends(get_db)):
    """Updates an existing tank configuration."""
    db_config = db.query(TankConfig).filter(TankConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update only provided fields
    data = update_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tank_config(config_id: int, db: Session = Depends(get_db)):
    """Deletes a tank configuration."""
    db_config = db.query(TankConfig).filter(TankConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(db_config)
    db.commit()
    return None
