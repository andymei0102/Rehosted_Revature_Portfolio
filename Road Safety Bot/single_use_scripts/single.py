from ultralytics import YOLO
import os
import torch
from dotenv import load_dotenv


def show_all_classnames():
    model1 = YOLO('drowsy_frozen.pt')
    model2 = YOLO('texting_frozen.pt')
    class_names1 = model1.names
    class_names2 = model2.names
    print("CLASS NAMES 1:", class_names1)
    print("CLASS NAMES 2:", class_names2)

def main():
    model = YOLO('drowsy_frozen.pt')

    results = model("./tst.jpg")[0]
    confs = results.boxes.conf.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy()
    print(confs, classes)
    class_names = results.names
    names = [class_names[class_index] for i, class_index in enumerate(classes) if confs[i] > 0.60]
    confs = [confs[i] for i, class_index in enumerate(classes) if confs[i] > 0.60]
    print("names:", names)
    print("confs:", confs)
    results[0].save(filename="output.jpg")

if __name__ == "__main__":
    main()
    #show_all_classnames()