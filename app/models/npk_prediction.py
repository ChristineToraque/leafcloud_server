from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from app.core.database import Base

class NPKPrediction(Base):
    __tablename__ = "npk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    daily_reading_id = Column(Integer, ForeignKey("daily_readings.id"))
    predicted_n = Column(Float)
    predicted_p = Column(Float)
    predicted_k = Column(Float)
    macro_scale = Column(Float)
    micro_scale = Column(Float)
    confidence_score = Column(Float)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
