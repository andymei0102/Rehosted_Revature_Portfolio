""" uses ultralytics solution to explain our models, generating heatmaps"""
import cv2
from ultralytics import solutions, YOLO

def generate_heatmap(model_name, image_path, output_path=None):
    # Load your model
    model = YOLO(model_name)

    # Load your image
    image = cv2.imread(image_path)

    # Initialize heatmap object
    heatmap = solutions.Heatmap(
        show=True,
        model=model,  # Pass the model directly
        colormap=cv2.COLORMAP_PARULA,
        # classes=[0, 2],  # Optional: specify classes for heatmap
    )

    # Run detection on the single image
    results = model(image)

    # Process the image with the heatmap
    processed_image = heatmap(image)

    # Display or save the result
    cv2.imshow("Heatmap", processed_image.plot_im)
    cv2.waitKey(0)
    cv2.imwrite(output_path, processed_image.plot_im)

if __name__ == "__main__":
    generate_heatmap("../texting_frozen.pt", "./texting.jpg", "texting_heatmap.jpg")
    generate_heatmap("../drowsy_frozen.pt", "./sleepy.jpg", "sleepy_heatmap.jpg")