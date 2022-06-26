from platform import release
import matplotlib.pyplot as plt
import cv2
import numpy as np
import threading, time
import pandas as pd
import detectron2
import torch, detectron2
import os, time
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
import cv2
import numpy as np
from detectron2.utils.logger import setup_logger
setup_logger()
import logging

### Detectron2 Model Setup

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = ("stop_sign_Train",)
#cfg.DATASETS.TEST = ()
cfg.DATASETS.TEST = ("stop_sign_Test",)
cfg.DATALOADER.NUM_WORKERS = 2

cfg.MODEL.WEIGHTS = r"C:\Users\max24\Downloads\model_final.pth"
# model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")  # Let training initialize from model zoo
cfg.SOLVER.IMS_PER_BATCH = 16  # This is the real "batch size" commonly known to deep learning people
cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
cfg.SOLVER.MAX_ITER = 2000    # 300 iterations seems good enough for this toy dataset; you will need to train longer for a practical dataset
cfg.SOLVER.CHECKPOINT_PERIOD = 500
cfg.TEST.EVAL_PERIOD = 100

# cfg.INPUT.MIN_SIZE_TRAIN = 50
# cfg.INPUT.MAX_SIZE_TEST = 640

cfg.SOLVER.STEPS = []        # do not decay learning rate
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1

cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.95   # set a custom testing threshold
predictor = DefaultPredictor(cfg)

### Video Capture

WIDTH = 640
HEIGHT = 480

cap = cv2.VideoCapture(0)
cap.set(3,WIDTH) # adjust width
cap.set(4,HEIGHT) # adjust height

### FPS Counter Setup
prev_frame_time = 0
new_frame_time = 0

RELATIVE_SIZE_TO_STOP = 0.2
FRAMES_TO_CONFIRM_START = 1
FRAMES_TO_CONFIRM_END = 5

def get_rect(coords, img):
    height = max(coords[0], coords[2]) - min(coords[0], coords[2])
    #width = max(coords[1], coords[3]) - min(coords[1], coords[3])
    
    img_height = img.shape[0]
    relative_size = height / img_height
    
    if relative_size > RELATIVE_SIZE_TO_STOP:
        return True, relative_size
    else:
        return False, relative_size


frames_with_sign = 0
frames_without_sign = 0
active = False

import requests, time

pi_url = "http://192.168.178.156:8000/run/"
video_url = "http://192.168.178.156:8765/mjpg"
cap = cv2.VideoCapture(video_url)

pi_forward = {"action": "forward"}
pi_backward = {"action": "backward"}
pi_stop = {"action": "stop"}

frame_rate = 7
prev = 0

def getSingleFrame():
        ret, image = cap.read()
        time.sleep(0.5)
        ret, jpeg = cv2.imencode('.jpg', image)
        stopVideo()
        return jpeg

def stopVideo():
        cap.release()



while True:
    time_elapsed = time.time() - prev

    if time_elapsed > 1./frame_rate:
        prev = time.time()

        # Measure FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        print("FPS:", fps)
        
        cap = cv2.VideoCapture(video_url)
        success, img = cap.read()
        cap.release()

        prediction = predictor(img)

        bboxes = prediction['instances'].pred_boxes.to('cpu').tensor.numpy()
        num_instances = len(bboxes)
        scores = prediction['instances'].scores.tolist()

        
        #print(bboxes, scores)
        if num_instances > 0:
            stop, relative_size = get_rect(bboxes[0], img)
        else:
            stop = False
            relative_size = ""

        border_color = [255, 0, 0]

        if stop:
            if active:
                frames_with_sign = FRAMES_TO_CONFIRM_START
                requests.get(pi_url, pi_stop)
            else:
                frames_with_sign += 1
            
            if frames_with_sign >= FRAMES_TO_CONFIRM_START:
                print("Stop confirmend")
                active = True
        else:
            frames_with_sign = 0
        
        if active and not stop:
            frames_without_sign += 1

        if frames_without_sign >= FRAMES_TO_CONFIRM_END:
            frames_without_sign = 0
            frames_with_sign = 0
            active = False
        
        if active:
            border_color = [0, 0, 255]
            requests.get(pi_url, pi_stop)
        else:
            if num_instances > 0:
                border_color = [255, 0, 0]
            else:
                requests.get(pi_url, pi_forward)
                border_color = [0, 255, 0]

        v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=2.0)
        out = v.draw_instance_predictions(prediction["instances"].to("cpu"))
        out_img = out.get_image()[:, :, ::-1]

        bordersize = 10
        out_img = cv2.copyMakeBorder(
            out_img,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=border_color
        )   
        
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (20,480)
        fontScale              = 0.8
        fontColor              = (255,255,255)
        thickness              = 1
        lineType               = 2

        cv2.putText(out_img, "FPS: " + str(fps), 
            (20,480), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

        if num_instances > 0:
            cv2.putText(out_img, "Relative Size: " + str(relative_size)[:4], 
                (350, 480), 
                font, 
                fontScale,
                fontColor,
                thickness,
                lineType)

        cv2.imshow("", out_img)
        
        
        if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
            cap.release()
            break

requests.get(pi_url, pi_stop)        
cv2.destroyAllWindows() 
cv2.waitKey(1)