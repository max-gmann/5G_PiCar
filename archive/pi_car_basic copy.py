from unittest import result
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import pandas as pd
import os, time
import cv2
import numpy as np
from detectron2.utils.logger import setup_logger
setup_logger()
import requests, time
import logging
import torch

### Video Capture

WIDTH = 640
HEIGHT = 480

cap = cv2.VideoCapture(0)
cap.set(3,WIDTH) # adjust width
cap.set(4,HEIGHT) # adjust height

### FPS Counter Setup
prev_frame_time = 0
new_frame_time = 0


model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom

# Inference



while True:
    success, img = cap.read()
    
    # FPS Counter
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)
    print("FPS:", fps)

    results = model(img)
    print(results)

    for instance in results.xyxy:
        try:
            label = results.names[int(instance.tolist()[0][-1])]
            bbox = instance.tolist()[0][:4]
            cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255,0,0), 2)
        except:
            pass

    cv2.imshow("", img)

    if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
        break
            
cv2.destroyAllWindows() 
cv2.waitKey(1)