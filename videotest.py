import  time
#import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
#import detectron2
#import torch, detectron2
import os, time
#from detectron2 import model_zoo
#from detectron2.engine import DefaultPredictor
#from detectron2.config import get_cfg
#from detectron2.utils.visualizer import Visualizer
#from detectron2.data import MetadataCatalog, DatasetCatalog
#from threading import Thread

#from detectron2.utils.logger import setup_logger
#setup_logger()
import logging
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.DEBUG)

from Pi_Car_Controls import pi_car
from Streaming_Controls import video_streamer

streamer = video_streamer(pi_car.video_url, fps_limit=30)
streamer.start()


while True:
    if streamer.next(logging=False):
        streamer.show()
        #frame = streamer.read()
        #frame = frame[240:480,0:640]
        low_b = np.uint8([50,50,50])
        high_b = np.uint8([0,0,0])
        #cv2.imshow("Frame",frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cv2.destroyAllWindows()
