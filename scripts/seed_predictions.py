import random
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import DailyReading, NPKPrediction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_predictions(limit: int = 100):
    """
    Generates dummy NPK predictions for testing purposes.
    Links them to existing daily_readings.
    """
    db = SessionLocal()
    try:
        # 1. Fetch readings that don't have predictions yet
        readings = db.query(DailyReading).outerjoin(NPKPrediction).filter(
            NPKPrediction.id == None
        ).limit(limit).all()

        if not readings:
            logger.info("No readings found that need predictions.")
            return

        logger.info(f"Seeding {len(readings)} predictions...")

        for reading in readings:
            # Generate random probabilities that sum to ~1.0
            p_water = random.uniform(0, 0.2)
            p_npk = random.uniform(0.3, 0.8)
            p_micro = random.uniform(0, 0.3)
            p_mix = 1.0 - (p_water + p_npk + p_micro)
            
            # Ensure p_mix is positive
            if p_mix < 0: p_mix = 0.05

            new_prediction = NPKPrediction(
                daily_reading_id=reading.id,
                predicted_n=round(p_npk, 4),    # Map NPK prob to N
                predicted_p=round(p_micro, 4),  # Map Micro prob to P
                predicted_k=round(p_mix, 4),    # Map Mix prob to K
                confidence_score=round(max(p_water, p_npk, p_micro, p_mix), 2),
                prediction_date=reading.timestamp
            )
            db.add(new_prediction)

        db.commit()
        logger.info("✅ Seeding complete.")

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # You can change the number of records to seed here
    seed_predictions(limit=500)
