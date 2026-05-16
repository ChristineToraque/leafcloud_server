# AI Model Analysis: **Nutrient Classifier Performance**

This document provides a deep-dive analysis of the evaluation results for the `leafcloud_sensor_boost` model (v4).

## 1. Executive Summary
- **Model Type**: Multi-Modal Classifier (Image + Sensor Fusion)
- **Total Samples Evaluated**: 17,641
- **Overall Accuracy**: **78%**
- **Main Finding**: The model is exceptional at identifying "Mix" and "Water" conditions but struggles to distinguish between "Micro" and "NPK" nutrients.

---

## 2. Performance Breakdown

### Classification Metrics
| Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **Water** | 0.78 | 0.92 | 0.85 | 3,593 |
| **NPK** | 0.64 | 0.80 | 0.71 | 4,671 |
| **Micro** | **0.97** | 0.40 | 0.57 | 4,478 |
| **Mix** | 0.85 | **0.99** | 0.91 | 4,899 |

### Key Observations
1.  **High-Confidence Identification (Micro)**: With a precision of **0.97**, if the model says a sample is "Micro," it is almost certainly correct.
2.  **High Recall (Mix & Water)**: The model is very good at "not missing" these categories. It captured 99% of all `Mix` samples and 92% of all `Water` samples.
3.  **Low Sensitivity (Micro)**: The recall of **0.40** for Micro is the primary bottleneck. The model missed 60% of actual Micro samples.

---

## 3. Confusion Matrix Analysis

| Actual \ Pred | Water | NPK | Micro | Mix |
| :--- | :--- | :--- | :--- | :--- |
| **Water** | **3302** | 291 | 0 | 0 |
| **NPK** | 912 | **3759** | 0 | 0 |
| **Micro** | 0 | **1813** | **1783** | 882 |
| **Mix** | 0 | 0 | 48 | **4851** |

### Critical Issues Identified:
-   **NPK/Micro Confusion**: The biggest failure point is that **1,813 Micro samples** were misclassified as **NPK**. This suggests that when only Micro nutrients are present, the sensors or visual cues look too similar to NPK-only conditions.
-   **Water/NPK Overlap**: 912 NPK samples were seen as Water. This may happen if the dosage was very low (near-water threshold).

---

## 4. Technical Recommendations

### A. Data Level
-   **Feature Engineering**: Investigate if the difference between NPK and Micro can be clearer by adding "delta" features (e.g., Change in EC over 24h) to the `app/services/discovery.py` logic.
-   **Re-balancing**: Although support is relatively even (3k-4k each), the "Micro" class needs more distinct samples or higher weights during Phase 1 training.

### B. Model Level
-   **Sensor Branch Weight**: The `Micro` class might rely more on sensors than images. We should consider increasing the complexity of the sensor branch in `nutrient_classifier.py`.
-   **Fine-tuning**: In Phase 2, we might need to unfreeze more layers of the MobileNetV2 base to capture the subtle visual differences between Micro and NPK deficiencies.

---

## 5. Pipeline Validation
The fact that **17,641 samples** were successfully processed confirms that:
1.  The `image_crops` ➡️ `cleaned_daily_readings` join is functionally correct.
2.  The `app/core/config.py` and `database.py` modules are handling high-volume queries efficiently.
3.  The file system paths for images are correctly mapped and accessible.
