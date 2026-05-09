from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from typing import List
from llm import *
from ultralytics import YOLO
import numpy as np
import cv2
import base64
import requests
import boto3
import json
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
drowsy_model = YOLO('model/drowsy_frozen.pt')
drowsy_model.model.eval()
texting_model = YOLO('model/texting_frozen.pt')
texting_model.model.eval()

drowsy_model.to(device)
texting_model.to(device)
print("Device:", device)

from logger import *

logger = setup_logger("api", "app_logs", True)

vision_model_router = APIRouter(
    prefix="/vision_model",
    tags=["vision_model"]
)

llm_model_router = APIRouter(
    prefix="/llm",
    tags=["llm"]
)

distraction_responses = []
drowsy_responses = []

texting_model_classes = ['c1: texting - right','c2: talking on the phone - right','c3: texting - left']
drowsy_model_classes = ['c4 - Drinking','c5 - Reaching Behind','d0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off', 'd3 - Eyes Open']

bad_classes = ['c1: texting - right', 'c3: texting - left','c2: talking on the phone - right', 'd0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off']

ENDPOINT_NAME = "tester"

@vision_model_router.post("/")
async def get_vision_response(files: List[UploadFile] = File(...)):
    sm = boto3.client('sagemaker-runtime', region_name='us-east-1')

    try:
        body = b"".join([await file.read() for file in files])

        response = sm.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/octet-stream",
            Body=body
        )
        result = response["Body"].read().decode("utf-8")
        # logger.info(f"SageMaker response: {result}")
        return json.loads(result)

    except Exception as e:
        logger.error(f"SageMaker error: {e}")
        return {"error": str(e)}
@vision_model_router.post("/local")
async def get_vision_response(files: List[UploadFile] = File(...)):
    """Returns response from driver detector model"""

    for file in files:
    # 1. Read the uploaded file bytes
        contents = await file.read()
        
        # 2. Convert bytes to a numpy array
        nparr = np.frombuffer(contents, np.uint8)
        
        # 3. Decode the array into an OpenCV image (the "frame")
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Could not decode image"}

        results_drowsy = drowsy_model(frame, conf=.70)[0]
        results_texting = texting_model(frame, conf=.70)[0]
        print(type(results_drowsy))
        sound_effect = False

        # 3. Use the built-in .summary() or structured access
        detections_drowsy = []
        detections = []

        for box in results_drowsy.boxes:
            class_id = int(box.cls[0])
            label_name = results_drowsy.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()


            if label_name in bad_classes:
                detections.append({
                    "label": label_name,
                    "confidence": confidence,
                    "box": [x1, y1, x2, y2]
                })
                return {
                    "beep": True,
                    "detections": detections
                }



        for box in results_texting.boxes:
            class_id = int(box.cls[0])
            label_name = results_texting.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            if label_name in bad_classes:
                detections.append({
                    "label": label_name,
                    "confidence": confidence,
                    "box": [x1, y1, x2, y2]
                })
                return {
                    "beep": True,
                    "detections": detections
                }
            
    #_,buffer = cv2.imencode('.jpg', results_texting.plot())
    return {"beep": False, "detections": []}
    #return {"beep": False, "result": base64.b64encode(buffer).decode('utf-8')}
@llm_model_router.get("/")
def get_llm_report(latitude, longitude):
    """Returns the route to the closest rest stop"""
    try: 
        response = safe_llm_call(latitude, longitude)
        logger.info("Successfully retrieved response")
    except Exception as e:
        logger.error(f"Unknown Exception Thrown: {e}")
    return response


app = FastAPI()

app.include_router(vision_model_router)
app.include_router(llm_model_router)





