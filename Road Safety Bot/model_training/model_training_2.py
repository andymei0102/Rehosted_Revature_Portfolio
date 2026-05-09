from ultralytics import YOLO
import os
import torch
from dotenv import load_dotenv


def main():
    load_dotenv()

    # path to our yaml file
    datapath = os.getenv("data2")
    print("found datapath:", datapath)

    # train on CUDA if available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("TRAINING ON:", device, "name:", torch.cuda.get_device_name(0))

    # load the YOLOv8 model
    # upgraded from n (nano) to s (small) for better performance
    model = YOLO('best_text_experimental.pt')

    # hyperparameters, change as you see fit this is a bit on the higher end
    num_epochs = 100
    num_workers = 4
    batch_size = 12

    # start training
    results = model.train(
        data=datapath,
        epochs=num_epochs,
        batch=batch_size,
        imgsz=640,
        patience=15,

        # Augmentations
        augment=True,
        hsv_h=0.05,
        hsv_s=0.25,
        hsv_v=0.25,

        fliplr=0.5,
        flipud=0.0,

        degrees=15,
        translate=0.1,
        scale=0.1,
        shear=5.0,

        mosaic=1.0,
        mixup=0.5,

        workers=num_workers,
        device=device
    )

if __name__ == "__main__":
    main()