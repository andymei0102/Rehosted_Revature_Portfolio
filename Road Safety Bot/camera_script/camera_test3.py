from ultralytics import YOLO
import cv2
from playsound import playsound
import time
import threading
import queue
import numpy as np
import base64
from logger import *
import geocoder
# ------------------- setup  -------------------
def beep():
    """
    Plays a beep sound to alert the driver of bad behavior.
    """
    threading.Thread(target=playsound, args=('beep.mp3',), daemon=True).start()

#texting_model = YOLO('texting_frozen.pt')
#awake_model = YOLO('drowsy_frozen.pt')

#texting_model.model.eval()
#awake_model.model.eval()

target_classes_model1 = ['c1: texting - right','c2: talking on the phone - right','c3: texting - left']
target_classes_model2 = ['c0 - Safe Driving','c4 - Drinking','c5 - Reaching Behind','d0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off', 'd3 - Eyes Open']
bad_classes = ['c1: texting - right', 'c3: texting - left','c2: talking on the phone - right', 'd0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off']

frame_queue = queue.Queue(maxsize=16)  # store frames for inference
result_queue = queue.Queue(maxsize=16)  # store results for drawing
stop_event = threading.Event()

last_beep_time = time.time()
BATCH_SIZE = 5

url = "http://localhost:8000"

# ------------------- Camera Thread -------------------
last_frame = None

def camera_thread():
    """
    Thread responsible for capturing frames from the camera and pushing them to the frame queue.

    After capturing a frame, it saves the latest raw frame to the global variable last_frame.

    If the frame queue is full, it tries to get the next frame without blocking. If the queue is empty, it continues to the next iteration.

    It then tries to get the processed frame from the result queue. If the result queue is empty, it falls back to the raw feed.

    Finally, it draws the detections on the frame and displays the frame using cv2.imshow.

    If the user presses 'q', it sets the stop event and breaks the loop, releasing the camera and destroying the window.
    """
    global last_frame
    cap = cv2.VideoCapture(0)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue

        # Save latest raw frame
        last_frame = frame.copy()

        # Push to queue
        if frame_queue.full():
            try:
                frame_queue.get_nowait() # get no wait, gets next without blocking
            except queue.Empty:
                pass
        frame_queue.put(frame)

        # Try to get processed frame
        display_frame = None
        try:
            display_frame = result_queue.get_nowait()
        except queue.Empty:
            display_frame = last_frame  # fallback to raw feed


        display_frame = draw_detections(display_frame, latest_detections)
        cv2.imshow("Camera Feed", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()

# ------------------- Inference Thread -------------------
import requests
import cv2

URL = "http://localhost:8000" # change this

def draw_detections(frame, detections):
    
    """
    Draws bounding boxes and labels on a given frame based on detections.

    Args:
        frame (numpy.ndarray): The frame to draw on.
        detections (list): A list of detections, where each detection is a dictionary containing the keys "box", "label", and "confidence".

    Returns:
        numpy.ndarray: The frame with the bounding boxes and labels drawn on it.
    """
    for det in detections:
        x1, y1, x2, y2 = map(int, det["box"])
        label = det["label"]
        conf = det["confidence"]

        color = (0, 0, 255) if label in bad_classes else (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    return frame

emails = setup_logger("api", "email_logs", True)

import smtplib
beep_count = 0

latest_detections = []
def inference_thread():
    global beep_count
    
    """
    Thread responsible for sending batches of frames to the vision model for inference.

    Every time the batch is full (i.e., when len(images) >= BATCH_SIZE), it sends a POST request to the vision model with the batch of frames.

    If the response is successful (i.e., status code 200), it checks if the response contains a "beep" key. If it does, it triggers a beep sound and resets the last beep time.

    If the response contains a "detections" key, it draws the bounding boxes and labels on the frame and puts the frame into the result queue.

    If the request fails, it prints an error message and clears the batch.

    This thread runs until the stop event is set.
    """
    global last_beep_time
    global latest_detections
    images = []

    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        # Encode frame as JPEG
        success, img_encoded = cv2.imencode('.jpg', frame)
        if not success:
            continue

        images.append(img_encoded.tobytes())

        # When batch is full → send request
        if len(images) >= BATCH_SIZE:
            print(f"Sending batch of {len(images)}")

            try:
                files = [
                    ('files', (f'frame_{i}.jpg', img, 'image/jpeg'))
                    for i, img in enumerate(images)
                ]

                response = requests.post(f"{URL}/vision_model/", files=files, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    print("Response:", data)

                    # send
                    trigger_beep = data["beep"]
                    if data["detections"]:
                        detections = data["detections"]
                        latest_detections = detections
                        f2 = frame.copy()
                        image_data = draw_detections(f2, detections)
                        result_queue.put(image_data) # put frame into queue

                    current_time = time.time()
                    if trigger_beep and (current_time - last_beep_time) >= 3: # only send once every 3 seconds max
                        beep()
                        beep_count += 1
                        last_beep_time = current_time

                else:
                    print("Bad response:", response.status_code)

            except Exception as e:
                print(f"Batch upload failed: {e}")

            # clear batch
            images = []
        '''
        # commented out due to performance issues
        if beep_count > 0:
            g = geocoder.ip('me')
            current_lat = g.latlng[0]
            current_lng = g.latlng[1]
            response = requests.get(
            f"{URL}/llm/",
            params={"latitude": current_lat, "longitude": current_lng}
            )
            emails.info(response.text)
        '''


if __name__ == '__main__':
    
    camera = threading.Thread(target=camera_thread)
    model_inference = threading.Thread(target=inference_thread, daemon=True)

    camera.start()
    model_inference.start()

    camera.join()
    model_inference.join()