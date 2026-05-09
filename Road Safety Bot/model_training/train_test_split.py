# basic script for me to split dataset because new dataset doesn't have train/val/test folders
import os
import random
import shutil


images_dir = "data/Distracted Driving Detection part 1.yolov8/train/images"
labels_dir = "data/Distracted Driving Detection part 1.yolov8/train/labels"

# Split ratios
train_ratio = 0.7
val_ratio = 0.15
test_ratio = 0.15

base_dir = "data/Distracted Driving Detection part 1.yolov8"

# Get image list
images = [f for f in os.listdir(images_dir) if f.endswith((".jpg", ".png", ".jpeg"))]
random.shuffle(images)

# Compute splits
total = len(images)
train_end = int(total * train_ratio)
val_end = train_end + int(total * val_ratio)

train_imgs = images[:train_end]
val_imgs = images[train_end:val_end]
test_imgs = images[val_end:]

def move_files(file_list, split):
    img_out = os.path.join(base_dir, f"images/{split}")
    lbl_out = os.path.join(base_dir, f"labels/{split}")

    os.makedirs(img_out, exist_ok=True)
    os.makedirs(lbl_out, exist_ok=True)

    for img in file_list:
        label = os.path.splitext(img)[0] + ".txt"

        shutil.move(os.path.join(images_dir, img), os.path.join(img_out, img))

        label_path = os.path.join(labels_dir, label)
        if os.path.exists(label_path):
            shutil.move(label_path, os.path.join(lbl_out, label))

# Move files
move_files(train_imgs, "train")
move_files(val_imgs, "val")
move_files(test_imgs, "test")

print(f"Done! Train: {len(train_imgs)}, Val: {len(val_imgs)}, Test: {len(test_imgs)}")