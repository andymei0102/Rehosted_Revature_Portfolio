# inference.py
import io
import json
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO
bad_classes = ['c1: texting - right', 'c3: texting - left','c2: talking on the phone - right', 'd0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off']

# loads both models
def model_fn(model_dir):
    """
    Loads both drowsy and texting models from model_dir

    Parameters
    ----------
    model_dir : str
        The directory containing the models

    Returns
    -------
    dict
        A dictionary containing the drowsy and texting models
    """
    drowsy_model = YOLO(f"{model_dir}/drowsy_frozen.pt")
    texting_model = YOLO(f"{model_dir}/texting_frozen.pt")
    drowsy_model.model.eval()
    texting_model.model.eval()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    drowsy_model.to(device)
    texting_model.to(device)

    return {
        "drowsy": drowsy_model,
        "texting": texting_model
    }


def extract_boxes(results, names):
    """
    Extracts bounding boxes from results and filters out bad classes

    Parameters
    ----------
    results : ultralytics.YOLO.Results
        The results from the YOLO model
    names : list
        A list of class names corresponding to the YOLO model

    Returns
    -------
    list
        A list of dictionaries containing the label, confidence, and bounding box coordinates
    """
    boxes = []

    if results.boxes is None:
        return boxes

    for b in results.boxes:
        cls_id = int(b.cls[0])
        label = names[cls_id]

        if label not in bad_classes: # ONLY APPEND THINGS THAT ARE CONSIDERED BAD
            continue

        x1, y1, x2, y2 = b.xyxy[0].tolist()
        conf = float(b.conf[0])

        boxes.append({
                    "label": label,
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
                    })

    return boxes

# read input (its image)
def input_fn(request_body, content_type='application/octet-stream'):
    """
    Reads an image from the request body and returns it as a numpy array.

    Parameters
    ----------
    request_body : bytes
        The request body containing the image data
    content_type : str, optional
        The content type of the request body, defaults to 'application/octet-stream'

    Returns
    -------
    numpy.ndarray
        The image data as a numpy array

    Raises
    ------
    ValueError
        If the content type is not supported
    """
    if content_type == 'application/octet-stream':
        image = Image.open(io.BytesIO(request_body)).convert("RGB")
        img = np.array(image)

        # Convert RGB → BGR (important for OpenCV/YOLO consistency)
        #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # getting mixed signals for if this is needed

        return img

    raise ValueError(f"Unsupported content type: {content_type}")


# predict on both
def predict_fn(input_data, models):
    """
    Predicts whether the driver is distracted or not based on the input image.

    Parameters
    ----------
    input_data : numpy.ndarray
        The input image data as a numpy array
    models : dict
        A dictionary containing the 'drowsy' and 'texting' models

    Returns
    -------
    dict
        A dictionary containing the results of the prediction
        The dictionary contains the following keys:
            'beep' : bool
                Whether the driver is distracted or not
            'detections' : list
                A list of bounding box coordinates and class labels

    """
    drowsy_model = models["drowsy"]
    texting_model = models["texting"]

    #results_drowsy = drowsy_model(input_data, conf=0.50)[0]
    #results_texting = texting_model(input_data, conf=0.50)[0]
    results_drowsy = drowsy_model.predict(input_data, conf=0.70)[0] # trying out different format
    results_texting = texting_model.predict(input_data, conf=0.70)[0]

    drowsy_boxes = extract_boxes(results_drowsy, drowsy_model.names)
    texting_boxes = extract_boxes(results_texting, texting_model.names)

    all_boxes = drowsy_boxes + texting_boxes

    # beep logic (same as before but cleaner)
    beep = len(all_boxes) > 0

    return {
        "beep": beep,
        "detections": all_boxes
    }


# output, dump straight to json
def output_fn(prediction, content_type='application/json'):
    """
    Outputs the predicted data in the specified content type.

    Parameters
    ----------
    predicted : dict
        The predicted data as a dictionary
    content_type : str, optional
        The content type to output the data in, default is 'application/json'

    Returns
    -------
    str
        The predicted data as a string in the specified content type
    """
    return json.dumps(prediction)