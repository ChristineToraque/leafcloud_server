# System Integration: **Multi-Task AI & Dashboard**

This document describes how the Multi-Task AI model (Classification + Regression) is integrated into the LeafCloud Server and how it communicates with the Farmer's Mobile App.

## 1. Data Flow Architecture

1.  **IoT Upload**: The Raspberry Pi uploads a wide-angle image and sensor data (pH, EC, Temp).
2.  **AI Processing**: `app/services/ai_service.py` runs the multi-task model on 5 image crops.
    -   **Classification**: Identifies the blend type (e.g., "Mix").
    -   **Regression**: Estimates concentration scales (Macro: 0.0-2.0, Micro: 0.0-2.0).
3.  **Sanity Check**: The system compares the Classification vs. Regression. If the AI sees "Water" but sensors/regression show "High Nutrients", `is_anomaly` is set to `True`.
4.  **Database Storage**: Results are saved in the `npk_predictions` table.
5.  **Dashboard API**: `app/api/v1/endpoints/iot.py` fetches the latest prediction and calculates physical grams and top-up requirements.

## 2. Database Schema (NPK Predictions)

| Column | Type | Description |
| :--- | :--- | :--- |
| `predicted_class` | String | The detected profile (Water, NPK, Micro, Mix). |
| `macro_scale` | Float | 0.0 to 2.0 (2.0 = 100% target dosage). |
| `micro_scale` | Float | 0.0 to 2.0 (2.0 = 100% target dosage). |
| `is_anomaly` | Boolean | True if visual data contradicts numerical data. |
| `confidence_score` | Float | AI confidence in the classification (0.0 - 1.0). |

## 3. Dashboard API Logic (`/dashboard/{tank_id}`)

### Profile Detection
The `profile_detected` field in the API response is now driven by the AI's visual classification:
- `Water` → "Water Only (No Nutrients)"
- `NPK` → "Macro-Leaning Blend"
- `Micro` → "Micro-Leaning Blend"
- `Mix` → "Balanced Mix"

### Anomaly Alerts
If `is_anomaly` is `True`, the API overrides the standard advisory:
- **Summary**: "AI Sensor Anomaly Detected"
- **Explanation**: Explains the conflict (e.g., AI sees Water, but Regression sees High Nutrients).
- **Action**: Advises manual inspection and sensor recalibration.

## 4. Mobile App Integration Requirements

To provide the best experience for the farmer, the mobile app should implement the following:

### A. Dynamic Status Card
- **Label**: Display `profile_detected` prominently.
- **Color**: Use `health_status` (`HEALTHY` = Green, `NUTRIENT DEFICIENT` = Orange).

### B. Anomaly Warning
- If `advisory.summary == "AI Sensor Anomaly Detected"`, display a warning banner at the top of the dashboard.
- This serves as a critical "Sanity Check" for the farmer.

### C. Nutrient Scales
- Use `estimated_nutrients` to show the remaining grams.
- If a top-up is required, display the `topup_macro_ml` and `topup_micro_ml` values from the `alert` object.

## 5. Maintenance
To retrain the model or update the logic:
- Training script: `scripts/nutrient_classifier_v2.py`
- Inference logic: `app/services/ai_service.py`
- API math: `app/api/v1/endpoints/iot.py`
