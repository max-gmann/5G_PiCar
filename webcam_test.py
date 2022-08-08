from abc import abstractclassmethod
import  time
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
import torch
import os, time
from threading import Thread

import logging
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.DEBUG)

from Pi_Car_Controls import pi_car
from Streaming_Controls import video_streamer, video_player

class obstacle():
    def __init__(self, name):
        self.name = name

    @abstractclassmethod
    def analyse_image(self, image):
        pass

    @abstractclassmethod
    def __get_control_output():
        pass

class stop_sign(obstacle):

    RELATIVE_SIZE_TO_STOP = 0.2

    FRAMES_TO_CONFIRM_START = 5
    FRAMES_TO_CONFIRM_END = 10
    WAIT_TIME = 4.0

    def __init__(self, model = "yolo"):
        super().__init__("stop_sign")

        self.__build_yolo_model()
        self.bboxes = [0,0,0,0]
        self.frames_seen = 0
        self.frames_not_seen = 0
        self.relative_size = None
        self.active = 0
        self.released = True
        self.wait_timer_start = None
        self.num_instances = 0
    

    def __build_yolo_model(self):
        self.predictor = torch.hub.load('ultralytics/yolov5', 'yolov5n')

    def __detect_stop_signs(self):
        self.prediction = self.predictor(self.image)
   
        for instance in self.prediction.xyxy:
            if len(instance.tolist()) != 0:
                label =  self.prediction.names[int(instance.tolist()[0][-1])]
                if label == "stop sign":
                    self.bboxes = instance.tolist()[0][:4]
                    self.num_instances = len(self.prediction.xyxy)

    def analyse_image(self, img, model_input_size = (640, 360)):
        
        # resize image
        resized = cv2.resize(img, model_input_size, interpolation = cv2.INTER_AREA)

        self.image = resized

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

        return self.__get_control_output(), self.bboxes, self.__get_color_code(), self.relative_size

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
        if self.bboxes is not [0,0,0,0]:
            box = self.bboxes
            height = max(box[0], box[2]) - min(box[0], box[2])
            
            img_height = self.image.shape[0]
            self.relative_size = round((height / img_height), 2)
        else:
            self.relative_size = 0.0


with pi_car(default_speed=30) as car:

    streamer = video_streamer(streaming_url =pi_car.video_url, 
                            fps_limit=1, 
                            print_logging = True)
    streamer.start()

    player = video_player(streamer.read())
    player.start()

    stop = stop_sign()

    while True:
        if streamer.next():
            current_img = streamer.read()


            t1 = time.time()
            control_output, bboxes, border_color, relative_size = stop.analyse_image(current_img)
            logging.debug(control_output)

            streamer.set_border_color(border_color)
            player.set_color(border_color)
            player.show_relative_size(relative_size)
            t2 = time.time()
            logging.debug(f"Processing time: {t2 - t1}s")

            player.update_img(current_img, bboxes)        

        if player.stopped or streamer.stopped: # quit when 'q' is pressed
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