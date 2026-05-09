from ultralytics import YOLO
import os
import torch
from dotenv import load_dotenv


def main():
    load_dotenv()

    # path to our yaml file
    datapath = os.getenv("data")
    print("found datapath:", datapath)

    # train on CUDA if available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("TRAINING ON:", device, "name:", torch.cuda.get_device_name(0))

    # load the YOLOv8 model
    # upgraded from n (nano) to s (small) for better performance
    model = YOLO('yolov8s.pt')

    # hyperparameters, change as you see fit this is a bit on the higher end
    num_epochs = 250
    num_workers = 12
    batch_size = 32

    # start training
    results = model.train(
        data=datapath,      # direct path to data.yaml
        epochs=num_epochs,
        batch=batch_size,
        imgsz=640,   # we got (640x480) images
        workers=num_workers,
        device=device
    )

if __name__ == "__main__":
    main()