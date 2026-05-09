import boto3
import time
from ultralytics import YOLO
def test_endpoint():
    sm = boto3.client("sagemaker-runtime", region_name="us-east-1")

    with open("explainability/texting.jpg", "rb") as f:
        img = f.read()

    response = sm.invoke_endpoint(
        EndpointName="tester",
        ContentType="application/octet-stream",
        Body=img
    )

    print(response["Body"].read().decode("utf-8"))


def test_model():
    model = YOLO("model/drowsy_frozen.pt")
    model2 = YOLO("model/texting_frozen.pt")
    model.to("cuda")
    model2.to("cuda")
    model.predict("explainability/texting.jpg")
    model2.predict("explainability/texting.jpg")
if __name__ == "__main__":
    start = time.time()
    test_endpoint()
    print("took:", time.time() - start)

    #start = time.time()
    #test_model()
    #print("took:", time.time() - start)