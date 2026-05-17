# Monitoring Dashboard: **Farmer's Interface**

This guide explains how the mobile app retrieves the real-time monitoring data for the farmer's dashboard.

## 1. Dashboard Endpoint
**URL**: `http://<server-ip>:8000/api/v1/iot/dashboard/{tank_id}`
**Method**: `GET`

---

## 2. Response Structure
The endpoint returns a complex JSON object that aggregates sensor telemetry, AI predictions, and physical math.

### A. Raw Sensor Telemetry
Direct readings from the Raspberry Pi sensors.
*   `ph`, `ec`, `water_temp`

### B. Estimated Nutrient Content (Physical Grams)
The backend automatically multiplies the AI's **Scaling Index** against the **Tank Configuration** (Volume and NPK %).
*   `n_grams`, `p_grams`, `k_grams`

### C. Visual Diagnostics
*   `image_url`: Path to the latest processed crop image.
*   `health_status`: `HEALTHY` or `NUTRIENT DEFICIENT`.
*   `profile_detected`: `Balanced`, `Macro-Leaning Blend`, or `Micro-Leaning Blend`.

### D. Actionable Alerts
If nutrient levels drop below 70%, the server generates a top-up instruction:
```json
"alert": {
  "level": "WARNING",
  "message": "Nutrient levels have dropped to 45% of recommended dosage.",
  "action_required": true,
  "topup_macro_ml": 3.0,
  "topup_micro_ml": 3.0
}
```

---

## 3. How the Math Works
The backend performs the following calculation on-the-fly:
1.  **AI Output**: Gets `macro_scale` (e.g., 0.5) from the AI model.
2.  **Config**: Gets `target_macro_dosage_mll` (e.g., 2.0 mL/L) and `water_volume_liters` (e.g., 6.0 L).
3.  **Physical Amount**: 
    - `Grams = (Scale * Dosage * Volume) * (NPK % / 100)`
    - `Top-up mL = (1.0 - Scale) * Dosage * Volume`

## 4. Mobile Implementation Example
The mobile app should call this endpoint every time the farmer opens the dashboard or refreshes the screen.
```javascript
const refreshDashboard = async (tankId) => {
  const response = await fetch(`http://192.168.1.20:8000/api/v1/iot/dashboard/${tankId}`);
  const data = await response.json();
  updateUI(data);
};
```
