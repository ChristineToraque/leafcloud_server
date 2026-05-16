# Database Model: **Daily Readings**

This document explains the schema and purpose of the `cleaned_daily_readings` table.

## 1. Overview
The `cleaned_daily_readings` table stores processed sensor data collected on a daily basis. This data is critical for our AI models (like the `nutrient_classifier.py`) as it provides the environmental context (pH, EC, Temperature) accompanying the crop images.

## 2. Table Schema

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BigInteger | Unique identifier (Primary Key). |
| `timestamp` | DateTime (TZ) | The exact date and time the reading was recorded. |
| `image_path` | String | Path to the crop image associated with this reading. |
| `ph` | Float | The pH level of the water. |
| `ec` | Float | The Electrical Conductivity of the water. |
| `water_temp` | Float | The temperature of the water in Celsius. |
| `experiment_id` | BigInteger | Reference to the specific experiment this reading belongs to. |

## 3. Performance (Indexes)
To ensure fast queries during data analysis and AI training, the following indexes are implemented:
*   `idx_cleaned_exp_id`: Optimizes lookups for readings belonging to a specific experiment.
*   `idx_cleaned_timestamp`: Optimizes time-series analysis and range-based queries.

## 4. Usage in AI Training
This table is the primary source of truth for the **Sensor-Boosted** AI logic. When training the `nutrient_classifier.py`, the script joins this table with `image_crops` to create a multi-modal dataset containing both visual and chemical data.

## 5. How to Query via SQL
You can use the provided utility script to check the latest readings:
```bash
./scripts/run-query.sh "SELECT * FROM cleaned_daily_readings ORDER BY timestamp DESC LIMIT 5;"
```
