from ultralytics import YOLO
import cv2
import requests
import numpy as np
# pip install geocoder
import geocoder

g = geocoder.ip('me')
current_lat = g.latlng[0]
current_lng = g.latlng[1]

# setup camera
cap = cv2.VideoCapture(0)

url = "http://localhost:8000"

frame_count = 0

images = []

while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break
    
    
    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 1. Encode the frame as a JPEG (converts NumPy array to bytes)
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        continue

    # 2. Convert to a buffer/bytes object
    image_bytes = encoded_image.tobytes()

    images.append(image_bytes)

    if len(images) >= 5:
        print(len(images))
        try:
            # Prepare the multi-file payload
            # Each tuple is: (form_field_name, (filename, bytes, content_type))
            files = [
                ('files', (f'frame_{i}.jpg', img, 'image/jpeg')) 
                for i, img in enumerate(images)
            ]
            
            response = requests.post(f"{url}/vision_model/", files=files)
            
            if response.status_code == 200:
                print(f"Successfully processed sample")
                print(response.json())
            
            # 3. CLEAR the batch to start over
            images = []
            
        except Exception as e:
            print(f"Batch upload failed: {e}")
            images = [] # Clear anyway to prevent overflow

     # Optional: Display locally
    cv2.imshow("Local Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()