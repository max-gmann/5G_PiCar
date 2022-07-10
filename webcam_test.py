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
from threading import Thread

from detectron2.utils.logger import setup_logger
setup_logger()
import logging
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.DEBUG)

from Pi_Car_Controls import pi_car
from Streaming_Controls import video_streamer


class visualizer():

    def __init__(self, streamer, enabled = True):
        self.streamer = streamer

        self.input_img = None
        self.last_frame = None
        self.v = None

        self.relative_size_text = None
        self.color = (100, 100, 100)

        self.enabled = enabled

        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def stop(self):
        self.stopped = True

    def read(self):
        if self.last_frame is None:
            return self.input_img
        else:
            return self.last_frame

    def update(self):
#        time.sleep(1)
        while True:
            if self.stopped is True:
                break
            if self.input_img is not None:

                if self.enabled:
                    self.draw_prediction()
                
                self.streamer.show(self.read())

                if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
                    self.stop()
                    break
    
    def update_img(self, img, prediction):
        self.input_img = img
        self.prediction = prediction

    def show_relative_size(self, text):
        self.relative_size_text = text

    def set_color(self, color):
        self.color = color

    def draw_prediction(self):
        bboxes = self.prediction['instances'].pred_boxes.to('cpu').tensor.numpy()
        num_instances = len(bboxes)
        if num_instances > 0:
            if num_instances > 1:
                scores = self.prediction['instances'].scores.tolist()
                index_highest_prob = scores.index(max(scores))
            else:
                index_highest_prob = 0

            box = bboxes[index_highest_prob]
            input = self.input_img.copy()
            self.last_frame = cv2.rectangle(
                input,
                (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), 
                self.color, 
                2)

            self.last_frame = cv2.putText(self.last_frame, "Stop-Sign", (int(box[0]), int(box[1]-8)),
                video_streamer.font, 
                0.4,
                self.color,
                1,
                video_streamer.lineType)
            
            if self.show_relative_size is not None:
                self.last_frame = cv2.putText(self.last_frame, f"{self.relative_size_text}", (int(box[0]), int(box[3]+ 10)),
                video_streamer.font, 
                0.4,
                self.color,
                1,
                video_streamer.lineType)
        else:
            self.last_frame = self.input_img
        



class obstacle():
    def __init__(self, name):
        self.name = name

class stop_sign(obstacle):

    RELATIVE_SIZE_TO_STOP = 0.2

    FRAMES_TO_CONFIRM_START = 5
    FRAMES_TO_CONFIRM_END = 10
    WAIT_TIME = 4.0

    def __init__(self):
        super().__init__("stop_sign")
        self.__build_model()
        self.frames_seen = 0
        self.frames_not_seen = 0
        self.relative_size = None
        self.active = 0
        self.released = True
        self.wait_timer_start = None

    def __build_model(self):
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        self.cfg.DATALOADER.NUM_WORKERS = 2
        self.cfg.MODEL.WEIGHTS = r"model_final.pth"
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.95   
        self.predictor = DefaultPredictor(self.cfg)

    def __detect_stop_signs(self):
        self.prediction = self.predictor(self.image)

        self.bboxes = self.prediction['instances'].pred_boxes.to('cpu').tensor.numpy()
        self.num_instances = len(self.bboxes) 

    def analyse_image(self, img):
        self.image = img

        self.__detect_stop_signs()

        if self.num_instances > 0:
            if self.active and self.released:
                pass
            else:
                self.__get_relative_size()
                if self.relative_size >= stop_sign.RELATIVE_SIZE_TO_STOP:
                    self.frames_seen += 1

                    if self.frames_seen > stop_sign.FRAMES_TO_CONFIRM_START:
                        self.active = True
                        self.__start_wait()

        elif self.active:
            self.frames_not_seen += 1
            if self.frames_not_seen > stop_sign.FRAMES_TO_CONFIRM_END:
                logging.debug("Stopsign deactivated.")
                self.active = False
                self.frames_not_seen = 0
                self.frames_seen = 0

        return self.__get_control_output(), self.prediction, self.__get_color_code(), self.relative_size

    def __get_color_code(self):
        if self.active and not self.released:
            return (0, 0, 255) # red
        if self.active and self.released:
            return (255, 0, 0) # blue
            #return (220, 208, 255) # lilac
        if self.released:
            return (0, 255, 0) # green

    def __get_control_output(self):
        now = time.time()
        if self.wait_timer_start is None:
            return "go"

        if (now - self.wait_timer_start) >= stop_sign.WAIT_TIME:
            logging.debug("Released.")
            self.released = True
            self.wait_timer_start = None
            
        if self.released is True:
            return "go"
        else:
            return "stop"        

    def __start_wait(self):
        if self.wait_timer_start is None:
            logging.debug("Stopsign active. Starting timer.")
            self.wait_timer_start = time.time()
            self.released = False

    def __get_relative_size(self):
        box = self.bboxes[0]
        height = max(box[0], box[2]) - min(box[0], box[2])
        
        img_height = self.image.shape[0]
        self.relative_size = round((height / img_height), 2)


# with pi_car(default_speed=30) as car:

streamer = video_streamer(streaming_url = 0, fps_limit=30)
streamer.start()

vis = visualizer(streamer, enabled=True)
vis.start() 

stop = stop_sign()

while True:
    if streamer.next(logging=False):
        current_img = streamer.read()
        control_output, prediction, border_color, relative_size = stop.analyse_image(current_img)
        logging.debug(control_output)

        streamer.set_border_color(border_color)
        vis.set_color(border_color)
        vis.show_relative_size(relative_size)

        vis.update_img(current_img, prediction)        

    if vis.stopped: # quit when 'q' is pressed
        streamer.close()
        break








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