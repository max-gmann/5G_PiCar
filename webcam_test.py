import  time
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
import detectron2
import torch, detectron2
import os, time
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

from detectron2.utils.logger import setup_logger
setup_logger()
import logging
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.DEBUG)

from Pi_Car_Controls import pi_car
from Streaming_Controls import video_streamer

### Detectron2 Model Setup

def build_model():
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.WEIGHTS = r"model_final.pth"
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.99   # set a custom testing threshold
    predictor = DefaultPredictor(cfg)
    return predictor

#predictor = build_model()


RELATIVE_SIZE_TO_STOP = 0.01
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


# with pi_car(default_speed=30) as car:
streamer = video_streamer(streaming_url = 0, fps_limit=24)

while True:
    if streamer.next():
        
        current_img = streamer.get_image()

        # Show Image
        streamer.show(current_img, overlay=True)

        if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
            streamer.close()
            break

    else:
        # do something while waiting for the next image
        pass






# while True:

    
        
#         cap = cv2.VideoCapture(video_url)
#         success, img = cap.read()
#         cap.release()

#         prediction = predictor(img)

#         bboxes = prediction['instances'].pred_boxes.to('cpu').tensor.numpy()
#         num_instances = len(bboxes)
#         scores = prediction['instances'].scores.tolist()

        
#         #print(bboxes, scores)
#         if num_instances > 0:
#             stop, relative_size = get_rect(bboxes[0], img)
#         else:
#             stop = False
#             relative_size = ""

#         border_color = [255, 0, 0]

#         if stop:
#             if active:
#                 frames_with_sign = FRAMES_TO_CONFIRM_START
                
                
#                 if timer_start is None:
#                     timer_start = time.time()

#                 now = time.time()
#                 if now - timer_start < 4:
#                     print(now - timer_start)
                    
#                     if now - timer_ignore > 2:
#                         requests.get(pi_url, pi_stop)
#                         timer_ignore = -99999999999999999999
#                 else:
#                     timer_ignore = time.time()
#                     timer_start = None

#             else:
#                 frames_with_sign += 1
            
#             if frames_with_sign >= FRAMES_TO_CONFIRM_START:
#                 print("Stop confirmend")
#                 active = True
#         else:
#             frames_with_sign = 0
        
#         if active and not stop:
#             frames_without_sign += 1

#         if frames_without_sign >= FRAMES_TO_CONFIRM_END:
#             frames_without_sign = 0
#             frames_with_sign = 0
#             active = False
        
#         if active:
#             border_color = [0, 0, 255]
#             requests.get(pi_url, pi_stop)
#         else:
#             if num_instances > 0:
#                 border_color = [255, 0, 0]
#                 requests.get(pi_url, pi_right)
#                 requests.get(pi_url, pi_forward)
#             else:
#                 requests.get(pi_url, pi_right)
#                 requests.get(pi_url, pi_forward)

#                 border_color = [0, 255, 0]

#         v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=2.0)
#         out = v.draw_instance_predictions(prediction["instances"].to("cpu"))
#         out_img = out.get_image()[:, :, ::-1]


#         if num_instances > 0:
#             cv2.putText(out_img, "Relative Size: " + str(relative_size)[:4], 
#                 (350, 480), 
#                 font, 
#                 fontScale,
#                 fontColor,
#                 thickness,
#                 lineType)

#         cv2.imshow("", out_img)
        
        
#         if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
#             streamer.close()
#             break