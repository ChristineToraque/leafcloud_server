This script, `nutrient_classifier.py`, is a **Multi-Modal Deep Learning Training Script**.
 Its primary purpose is to train an AI model that predicts the type of nutrient or condition of a crop using both images and sensor data.

Here is a breakdown of what it does:

### 1. **Multi-Modal Data Input (Fusion)**
Unlike a standard image classifier, this script uses two different types of data simultaneously:
*   **Images**: It uses `MobileNetV2` (a pre-trained computer vision model) to analyze crop images.
*   **Sensors**: It takes 3 numeric sensor values: **pH**, **Electrical Conductivity (EC)**, and **Water Temperature**.
*   **The "Boost"**: It concatenates (fuses) the image features with the sensor data in a hidden layer to make a more accurate prediction.

### 2. **What it Predicts**
It is a **4-class classification** model. It tries to categorize the crops into one of these labels:
1. `Water`
2. `NPK` (Nitrogen, Phosphorus, Potassium)
3. `Micro` (Micronutrients)
4. `Mix`

### 3. **The Training Process**
*   **Database Integration**: It connects to your PostgreSQL database (using your `.env` settings) to fetch image paths and their corresponding sensor readings.
*   **Data Preprocessing**: It normalizes sensor data and resizes images to `224x224`. It also applies **Data Augmentation** (flips, brightness, contrast) to make the model more robust.
*   **Transfer Learning**: 
    *   **Phase 1**: It freezes the pre-trained `MobileNetV2` layers and trains only the new "head" of the model.
    *   **Phase 2 (Fine-tuning)**: It unfreezes the top 30 layers of the image model to refine the predictions.
*   **Output**: It saves the final trained model as a `.keras` file with a timestamp.

### 4. **SOLID Recommendation**
Since you want to adhere to SOLID principles, you should keep this file in the `scripts/` directory as it is a **heavy development/research utility**. 

However, once you are ready to use this model in the server (e.g., creating an API endpoint like `POST /api/v1/predict`), you should:
1.  Put the **Prediction Logic** in `app/services/prediction.py`.
2.  Store the `.keras` model file in an `assets/` or `models/` folder.
3.  Keep the **Training Logic** separate in `scripts/`.

[Next](./feature-2.md)