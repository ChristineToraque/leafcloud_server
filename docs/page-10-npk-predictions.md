# Database Model: **NPK Predictions**

This document explains the schema and purpose of the `npk_predictions` table.

## 1. Overview
The `npk_predictions` table stores the numerical outputs from our NPK estimation models (Regression). While the `nutrient_classifier.py` categorizes crops into buckets, future regression models will use this table to store specific estimated concentrations for Nitrogen (N), Phosphorus (P), and Potassium (K).

## 2. Table Schema

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Unique identifier (Primary Key). |
| `daily_reading_id` | Integer | Foreign key linking to the parent `daily_readings` record. |
| `predicted_n` | Float | Estimated Nitrogen concentration. |
| `predicted_p` | Float | Estimated Phosphorus concentration. |
| `predicted_k` | Float | Estimated Potassium concentration. |
| `confidence_score` | Float | The AI model's confidence in this specific prediction (0.0 to 1.0). |
| `prediction_date` | DateTime (TZ) | Timestamp of when the prediction was generated. |

## 3. Relationships
- **Daily Reading**: Each prediction is tied to a specific daily reading. This allows us to compare the AI's predicted NPK values against the actual sensor readings (pH, EC, Temp) and the experimental target ratios defined in the `experiments` table.

## 4. Future Integration
When the regression model is implemented, it will perform a "Multi-Output" prediction. The results will be saved here to track the nutritional health of the crops over time.

## 5. Verification
Check the latest predictions:
```bash
./scripts/run-query.sh "SELECT predicted_n, predicted_p, predicted_k, confidence_score FROM npk_predictions ORDER BY prediction_date DESC LIMIT 5;"
```
