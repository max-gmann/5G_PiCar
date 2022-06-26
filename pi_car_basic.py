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
import logging

### Video Capture

WIDTH = 640
HEIGHT = 480

cap = cv2.VideoCapture(0)
cap.set(3,WIDTH) # adjust width
cap.set(4,HEIGHT) # adjust height

### FPS Counter Setup
prev_frame_time = 0
new_frame_time = 0

import requests, time

pi_url = "http://192.168.178.156:8000/run/"
video_url = "http://192.168.178.156:8765/mjpg"
cap = cv2.VideoCapture(video_url)

pi_forward = {"action": "forward"}
pi_backward = {"action": "backward"}
pi_stop = {"action": "stop"}


while True:
    
    cap = cv2.VideoCapture(video_url)
    success, img = cap.read()
    cap.release()
    
    # FPS Counter
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)
    print("FPS:", fps)

    #requests.get(pi_url, pi_stop)
    #requests.get(pi_url, pi_forward)

    cv2.imshow("", img)
    
    if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
        break

requests.get(pi_url, pi_stop)        
cv2.destroyAllWindows() 
cv2.waitKey(1)