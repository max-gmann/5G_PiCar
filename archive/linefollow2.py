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

streamer = video_streamer(streaming_url = 0, fps_limit=30)
#streamer = video_streamer(pi_car.video_url, fps_limit=25)
streamer.start()

#car = pi_car(default_speed=30)
#time.sleep(3)
#car.forward()

#car.stop()


# i=1
# while True:
#     if streamer.next(logging=True):
#         i+=1
#         streamer.add_overlay
#         streamer.show()
#         print(i)
#         if cv2.waitKey(1) & 0xff == ord('q'):
#             break
# cv2.destroyAllWindows()

#car.forward()

while True:
    if streamer.next(logging=False):
        frame = streamer.read()
        streamer.add_overlay
        #frame = frame[80:400, 0:1000]
        low_b = np.uint8([60,60,60])
        high_b = np.uint8([0,0,0])
        mask = cv2.inRange(frame, high_b, low_b)
        contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        cv2.imshow("Mask",mask)
        cv2.imshow("Frame",frame)
        if len(contours) > 0 :
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] !=0 :
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                print("CX : "+str(cx)+"  CY : "+str(cy))
                if cx >= 560: 
                    print("Rechts")
                    #car.right()
                if cx < 560 and cx > 480: 
                    print("leicht Rechts")
                    #car.right()
                if cx < 480 and cx > 420: 
                    print("sehr leicht Rechts")
                    #car.right()
                if cx < 420 and cx > 240:
                    print("Auf der Strecke")
                    #car.straight()
                if cx < 240 and cx > 160:
                    print("sehr leicht Links")
                    #car.left()
                if cx < 160 and cx > 80:
                    print("leicht Links")
                    #car.left()    
                if cx <= 80:
                    print("Links")
                    #car.left()
                cv2.circle(frame,(cx,cy),5, (255,255,255), -1)
            cv2.drawContours(frame, c, -1,(0,255,0), 1)
            
            if cv2.waitKey(1) & 0xff == ord('q'):
                #car.stop()
                break
#car.stop()            
cv2.destroyAllWindows()




#         current_img = streamer.read()
#         streamer.get_image()
#         streamer.show()
 

#     if vis.stopped: # quit when 'q' is pressed
#         streamer.close()
#         break

# while True:
#     ret, frame = cap.read()
#     low_b = np.uint8([5,5,5])
#     high_b = np.uint8([0,0,0])
#     mask = cv2.inRange(frame, high_b, low_b)
#     contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
#     if len(contours) > 0 :
#         c = max(contours, key=cv2.contourArea)
#         M = cv2.moments(c)
#         if M["m00"] !=0 :
#             cx = int(M['m10']/M['m00'])
#             cy = int(M['m01']/M['m00'])
#             print("CX : "+str(cx)+"  CY : "+str(cy))
#             if cx >= 120 :
#                 print("Turn Left")
#                 GPIO.output(in1, GPIO.HIGH)
#                 GPIO.output(in2, GPIO.LOW)
#                 GPIO.output(in3, GPIO.LOW)
#                 GPIO.output(in4, GPIO.HIGH)
#             if cx < 120 and cx > 40 :
#                 print("On Track!")
#                 GPIO.output(in1, GPIO.HIGH)
#                 GPIO.output(in2, GPIO.LOW)
#                 GPIO.output(in3, GPIO.HIGH)
#                 GPIO.output(in4, GPIO.LOW)
#             if cx <=40 :
#                 print("Turn Right")
#                 GPIO.output(in1, GPIO.LOW)
#                 GPIO.output(in2, GPIO.HIGH)
#                 GPIO.output(in3, GPIO.HIGH)
#                 GPIO.output(in4, GPIO.LOW)
#             cv2.circle(frame, (cx,cy), 5, (255,255,255), -1)
#     else :
#         print("I don't see the line")
#         GPIO.output(in1, GPIO.LOW)
#         GPIO.output(in2, GPIO.LOW)
#         GPIO.output(in3, GPIO.LOW)
#         GPIO.output(in4, GPIO.LOW)
#     cv2.drawContours(frame, c, -1, (0,255,0), 1)
#     cv2.imshow("Mask",mask)
#     cv2.imshow("Frame",frame)
#     if cv2.waitKey(1) & 0xff == ord('q'):   # 1 is the time in ms
#         GPIO.output(in1, GPIO.LOW)
#         GPIO.output(in2, GPIO.LOW)
#         GPIO.output(in3, GPIO.LOW)
#         GPIO.output(in4, GPIO.LOW)
#         break
# cap.release()
# cv2.destroyAllWindows()