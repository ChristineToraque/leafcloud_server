# Database Model: **Raw Daily Readings**

This document explains the schema and purpose of the `daily_readings` table.

## 1. Overview
The `daily_readings` table stores the raw sensor data and image references as they are initially collected. This serves as the source data for the "cleaned" versions used in AI training.

## 2. Table Schema

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Unique identifier (Primary Key). |
| `timestamp` | DateTime (TZ) | Record creation time (Defaults to `now()`). |
| `image_path` | String(255) | Path to the raw crop image. |
| `ph` | Float | Raw pH reading. |
| `ec` | Float | Raw EC reading. |
| `water_temp` | Float | Raw water temperature reading. |
| `status` | String(50) | Status of the reading (e.g., processed, pending). |
| `experiment_id` | Integer | Link to the experiment. |

## 3. Implementation Details
*   **Automatic Timestamps**: The `timestamp` field is automatically populated by the database using `func.now()`.
*   **Indexing**: The `id` column is indexed for rapid primary key lookups.
*   **Exclusions**: Note that internal tracking columns like `ph_is_estimated` and `needs_ph_update` are intentionally excluded from this model to keep the API layer focused on core data.

## 4. Relationship to Cleaned Data
Data from this table is typically processed (outlier removal, normalization) and then stored in the `cleaned_daily_readings` table for use by the `nutrient_classifier.py`.
