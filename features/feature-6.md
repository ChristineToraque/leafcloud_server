# Code Walkthrough: `nutrient_classifier.py`

This document provides a detailed, step-by-step breakdown of the AI training pipeline.

## 1. Entry Point: `if __name__ == '__main__':`
The execution starts at the bottom of the script. 

1.  **Data Fetching**: It calls `get_dataset()` to pull all linked images and sensor data from PostgreSQL.
2.  **Splitting**: It performs an 80/20 split. 80% of the data goes to `train_gen` (for learning) and 20% to `val_gen` (for testing accuracy during training).
3.  **Model Building**: Calls `build_model_sensor_boosted()` to create the dual-input neural network.
4.  **Training Phase 1**: Trains only the top layers to avoid destroying the pre-trained knowledge in MobileNetV2.
5.  **Training Phase 2 (Fine-tuning)**: Unfreezes specific layers of the image model to allow it to "specialize" in plant features.
6.  **Saving**: Exports the final weights to a `.keras` file.

---

## 2. Data Acquisition: `get_dataset()`
This block handles the bridge between the database and the AI.

*   **The Query**: It performs a 3-way join: `image_crops` ➡️ `cleaned_daily_readings` ➡️ `experiments`. This ensures every image is paired with its specific pH, EC, and Water Temp.
*   **Normalization**: Raw sensor values (e.g., pH 5.5 to 7.0) are scaled between **0 and 1**. Neural networks perform significantly better with small, normalized numbers.
*   **Sample Weighting**: If you have 5,000 "Water" samples but only 1,000 "Micro" samples, the model might become biased. This block calculates "Sample Weights" so the model pays 5x more attention to the rarer categories.

---

## 3. The Engine: `MultiModalGenerator`
Because 17,000 images are too large to fit in computer memory (RAM) at once, we use a **Generator**.

*   **`__getitem__`**: This is called every time the AI needs a "Batch" of data. It loads 32 images and 32 sensor sets from the disk on-the-fly.
*   **Image Preprocessing**: It converts raw JPEGs into 224x224 arrays and applies `preprocess_input` (scaling pixels to the -1 to 1 range).
*   **Augmentation**: During training, it randomly flips or adjusts the brightness of images. This "fools" the AI into thinking it's seeing new data, preventing it from just memorizing the training set (Overfitting).

---

## 4. Architecture: `build_model_sensor_boosted()`
This is the "brain" of the system, using a **Functional API** approach.

### Branch A: Image Processor (MobileNetV2)
- Takes the (224, 224, 3) image input.
- Uses **Transfer Learning**: It starts with weights learned from millions of generic images (ImageNet).
- **GlobalAveragePooling2D**: Flattens the complex 3D image features into a 1D vector of 1280 "visual signals."

### Branch B: Sensor Processor (Dense Layers)
- Takes the (3,) sensor input (pH, EC, Temp).
- Uses **BatchNormalization** to keep the sensor signals stable during training.
- Outputs a 64-unit "chemical signal."

### The Fusion: `Concatenate`
- This is the "Boost" part. It glues the visual signals and chemical signals together into one large vector.
- This allows the AI to "think" like this: *"The image looks like a healthy leaf, BUT the EC sensor is very high, so it's actually a Mix nutrient solution."*

---

## 5. Decision Layer
The fused signals pass through a final `Dense(4, activation='softmax')` layer.
- **4 units**: One for each category (Water, NPK, Micro, Mix).
- **Softmax**: Ensures the 4 outputs add up to 100%. The highest percentage is the model's final "guess."
