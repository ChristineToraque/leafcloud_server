# IoT Integration: **Raspberry Pi to Server**

This guide explains how your Raspberry Pi can upload sensor data and images to the LeafCloud Server V2.

## 1. Upload Endpoint
**URL**: `http://<server-ip>:8000/api/v1/iot/upload`
**Method**: `POST`
**Content-Type**: `multipart/form-data`

---

## 2. Request Parameters
The Raspberry Pi must send the following fields in a **Multipart** request:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `tank_id` | Integer (Form) | The ID of the Tank/Bucket being monitored. |
| `ph` | Float (Form) | Current pH sensor reading. |
| `ec` | Float (Form) | Current EC sensor reading. |
| `temp` | Float (Form) | Current Water Temperature reading. |
| `image` | File | The JPEG image captured by the Pi Camera. |

---

## 3. Server Workflow
1.  **Instant Response**: The server saves the image and sensor data to the database immediately and returns a "Success" response to the Pi.
2.  **Background Processing**: After responding to the Pi, the server automatically starts the following in the background:
    -   **Auto-Cropping**: Segments the plant image into grids and filters them by greenness.
    -   **AI Prediction**: Runs the multi-modal AI model (Images + Sensors) to estimate nutrient levels.
    -   **Result Storage**: Saves the AI results into the `npk_predictions` table.

---

## 4. Raspberry Pi Example (Python/Requests)

```python
import requests

SERVER_URL = "http://192.168.1.20:8000/api/v1/iot/upload"

def upload_data(image_path, ph, ec, temp, tank_id=1):
    with open(image_path, 'rb') as img_file:
        files = {'image': img_file}
        data = {
            'tank_id': tank_id,
            'ph': ph,
            'ec': ec,
            'temp': temp
        }
        
        try:
            response = requests.post(SERVER_URL, files=files, data=data)
            if response.ok:
                # response contains: {"status": "success", "reading_id": <int>}
                print("Data uploaded successfully:", response.json())
            else:
                print("Upload failed:", response.text)
        except Exception as e:
            print("Connection error:", e)

# Usage
upload_data("plant_snapshot.jpg", 6.5, 1.2, 25.5)
```

## 5. Why use `tank_id`?
By sending a `tank_id`, the Raspberry Pi doesn't need to know anything about "Experiments" or "Bucket Labels." You can change the fertilizer profile or the tank name on the **Mobile Dashboard**, and the server will automatically use those settings for the incoming data from that specific Pi.
