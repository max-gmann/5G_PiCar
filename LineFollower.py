import cv2
from matplotlib import offsetbox
import numpy as np

class LineFollower():
    def __init__(self) -> None:
        self.low_b = np.uint8([60,60,60])
        self.high_b = np.uint8([0,0,0])
        # self.low_b = np.uint8([200,200,200])
        # self.high_b = np.uint8([255,255,255])
        self.crop_factor = 0.75
        
        self.steering_angle = 0
        self.lenkangschlag = 45 # maximum

        self.cx = 0
        self.cy = 0

    def __crop_frame(self, image):
        image = image.copy()
        height, width, _ = image.shape
        new_height = int(height * self.crop_factor)
        return image[new_height:height, 0:width], new_height

    def get_streering_angle(self, frame):
        cropped_frame, offset = self.__crop_frame(frame)
        cv2.imshow("debug", cropped_frame)
        mask = cv2.inRange(cropped_frame, self.high_b, self.low_b)
        contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0 :
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] !=0 :
                self.cx = int(M['m10']/M['m00'])
                self.cy = int(M['m01']/M['m00']) + offset
                # print("CX : "+str(cx)+"  CY : "+str(cy))

                frame_height, frame_width, _ = frame.shape
                # 0 = mitte des bildes
                print("frame width", frame_width)
                print("cx", self.cx)
                relative_position = self.cx / (frame_width / 2) -1
                print("relative position", relative_position)

                self.steering_angle = int(self.lenkangschlag * relative_position)
                
                print("Steering angle:", self.steering_angle)

                # if cx >= 560: 
                #     print("Rechts")
                #     #car.right()
                # if cx < 560 and cx > 480: 
                #     print("leicht Rechts")
                #     #car.right()
                # if cx < 480 and cx > 420: 
                #     print("sehr leicht Rechts")
                #     #car.right()
                # if cx < 420 and cx > 240:
                #     print("Auf der Strecke")
                #     #car.straight()
                # if cx < 240 and cx > 160:
                #     print("sehr leicht Links")
                #     #car.left()
                # if cx < 160 and cx > 80:
                #     print("leicht Links")
                #     #car.left()    
                # if cx <= 80:
                #     print("Links")
                #     #car.left()f

                # debug line

                # cv2.drawContours(frame, c, -1,(0,255,0), 1)
            
        
        
        return self.steering_angle

    def draw_annotations(self, frame):
        frame_height, frame_width, _ = frame.shape

        cv2.circle(frame,(self.cx,self.cy),5, (255,255,255), -1)
        cv2.line(frame, (self.cx,self.cy), (int(frame_width / 2), frame_height), color=(48, 22, 198), thickness=4)
        cv2.line(frame, (0, int(frame_height * self.crop_factor)), (frame_width, int(frame_height * self.crop_factor)), color=(255,0,0), thickness=2)