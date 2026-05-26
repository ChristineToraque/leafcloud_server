import sys
import os
# Auto-resolve parent directory to allow running the script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from app.services.ai_service import process_iot_data_background

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
            tank = tanks[0]  # always seed for the first tank when testing
            source_image = random.choice(all_images)

            now = datetime.now()
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


def seed_predictions():
    """
    Runs the real AI model on the latest daily_reading that doesn't have a prediction yet.
    """
    db = SessionLocal()
    try:
        reading = db.query(DailyReading).outerjoin(NPKPrediction).filter(
            NPKPrediction.id == None
        ).order_by(DailyReading.timestamp.desc()).first()

        if not reading:
            logger.info("No readings found that need predictions.")
            return

        logger.info(f"Running AI prediction for reading ID {reading.id}...")
    finally:
        db.close()

    process_iot_data_background(reading.id)
    logger.info("✅ AI prediction complete.")


if __name__ == "__main__":
    seed_daily_readings(count=1)
    seed_predictions()
