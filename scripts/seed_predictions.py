import random
import logging
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from app.core.database import SessionLocal
from app.core.config import settings
from app.models import DailyReading, NPKPrediction
from app.models.tank_config import TankConfig

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def seed_daily_readings(count: int = 50):
    """
    Simulates Raspberry Pi uploads by copying random images from images/captures/
    and creating daily_readings rows with randomized sensor values.
    """
    db = SessionLocal()
    try:
        source_dir = Path(settings.SOURCE_DIR) / "captures"
        all_images = list(source_dir.glob("*.jpg"))
        if not all_images:
            logger.error(f"No source images found in {source_dir}")
            return

        tanks = db.query(TankConfig).all()
        if not tanks:
            logger.error("No tanks found in DB")
            return

        logger.info(f"Seeding {count} daily readings...")
        created = 0

        for _ in range(count):
            tank = random.choice(tanks)
            source_image = random.choice(all_images)

            now = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            date_str = now.strftime("%Y-%m-%d")
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")

            folder_path = Path(settings.SOURCE_DIR) / date_str / tank.tank_name.replace(" ", "_")
            folder_path.mkdir(parents=True, exist_ok=True)

            filename = f"reading_{timestamp_str}_{uuid.uuid4().hex[:6]}.jpg"
            dest_path = folder_path / filename
            shutil.copy2(source_image, dest_path)

            reading = DailyReading(
                timestamp=now,
                image_path=str(dest_path).replace("\\", "/"),
                ph=round(random.uniform(5.5, 7.0), 2),
                ec=round(random.uniform(0.8, 2.5), 2),
                water_temp=round(random.uniform(24.0, 29.0), 1),
                tank_id=tank.id,
                is_new_data=True,
                status="pending"
            )
            db.add(reading)
            created += 1

        db.commit()
        logger.info(f"✅ Created {created} daily readings.")

    except Exception as e:
        logger.error(f"Error seeding daily readings: {e}")
        db.rollback()
    finally:
        db.close()


def seed_predictions(limit: int = 500):
    """
    Generates dummy NPK predictions for daily_readings that don't have one yet.
    """
    db = SessionLocal()
    try:
        readings = db.query(DailyReading).outerjoin(NPKPrediction).filter(
            NPKPrediction.id == None
        ).limit(limit).all()

        if not readings:
            logger.info("No readings found that need predictions.")
            return

        logger.info(f"Seeding {len(readings)} predictions...")

        for reading in readings:
            p_water = random.uniform(0, 0.2)
            p_npk = random.uniform(0.3, 0.8)
            p_micro = random.uniform(0, 0.3)
            p_mix = 1.0 - (p_water + p_npk + p_micro)
            if p_mix < 0:
                p_mix = 0.05

            new_prediction = NPKPrediction(
                daily_reading_id=reading.id,
                predicted_n=round(p_npk, 4),
                predicted_p=round(p_micro, 4),
                predicted_k=round(p_mix, 4),
                confidence_score=round(max(p_water, p_npk, p_micro, p_mix), 2),
                prediction_date=reading.timestamp
            )
            db.add(new_prediction)

        db.commit()
        logger.info("✅ Predictions seeded.")

    except Exception as e:
        logger.error(f"Error seeding predictions: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_daily_readings(count=50)
    seed_predictions(limit=500)
