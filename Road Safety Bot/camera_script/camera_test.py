from ultralytics import YOLO
import cv2
from playsound import playsound
import time
import threading

def beep():
    threading.Thread(target=playsound, args=('beep.mp3',), daemon=True).start()

# initialize yolov8 model
#model = YOLO('yolov8n.pt') # downloads model if you don't have by default


#texting_model = YOLO('best_text_medium.pt') # uses our best model from training for texting
texting_model = YOLO('texting_frozen.pt')
awake_model = YOLO('drowsy_frozen.pt')

texting_model.model.eval()
awake_model.model.eval()

target_classes_model1 = ['c1: texting - right','c2: talking on the phone - right','c3: texting - left']
target_classes_model2 = ['c0 - Safe Driving','c4 - Drinking','c5 - Reaching Behind','d0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off', 'd3 - Eyes Open']

bad_classes = ['c1: texting - right', 'c3: texting - left','c2: talking on the phone - right', 'd0 - Eyes Closed','d1 - Yawning','d2 - Nodding Off']

# setup camera
cap = cv2.VideoCapture(0)

last_beep_time = time.time()
while cap.isOpened():
    trigger_beep = False
    ret, frame = cap.read()
    if not ret:
        break
    results1 = texting_model(frame, conf=.60)
    results2 = awake_model(frame, conf=.60)
    #print(results1, results2)

    
    # filter out unwated classes
    filtered_results1 = []
    for det in results1[0].boxes:
        if results1[0].names[int(det.cls)] in bad_classes:
            trigger_beep = True
        if results1[0].names[int(det.cls)] in target_classes_model1:
            #print("here")
            filtered_results1.append(det)
    results1[0].boxes = filtered_results1

    filtered_results2 = []
    for det in results2[0].boxes:
        if results2[0].names[int(det.cls)] in bad_classes:
            trigger_beep = True
        #print("TEST:", results2[0].names[int(det.cls)])
        if results2[0].names[int(det.cls)] in target_classes_model2:
            #print("HYERE")
            filtered_results2.append(det)
    results2[0].boxes = filtered_results2
    
    current_time = time.time()
    # play beep.mp3 if driver is doing something bad
    if trigger_beep and (current_time - last_beep_time) >= 3:
        beep()

    # Draw results
    frame1 = results1[0].plot()  # model1 boxes
    frame2 = results2[0].plot()  # model2 boxes

    # combine visually by overlaying
    combined = cv2.addWeighted(frame1, 0.5, frame2, 0.5, 0)
    #combined = frame2
    # Show the result
    cv2.imshow("Two YOLO Models", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        playsound('beep.mp3')
        break

cap.release()
cv2.destroyAllWindows()