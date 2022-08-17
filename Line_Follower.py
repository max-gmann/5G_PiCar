import cv2
from matplotlib import offsetbox
import numpy as np

class LineFollower():
    def __init__(self) -> None:
        # Werte zum Folgen einer dunklen Linie
        # self.low_b = np.uint8([60,60,60])
        # self.high_b = np.uint8([0,0,0])
        # Werte zum Folgen einer hellen Linie
        self.threshold_dark = 70
        self.threshold_light = 220
        self.crop_factor = 0.70
        
        #Lenkwinkel
        self.steering_angle = 0
        self.lenkangschlag = 45 # maximum

        self.cx = 0
        self.cy = 0
        
        #Dient zum zurechtschneiden des erhalten Bildmaterials
    def __crop_frame(self, image):
        image = image.copy()
        height, width, _ = image.shape
        new_height = int(height * self.crop_factor)
        return image[new_height:height, 0:width], new_height

    #ermittelt den notwendigen Lenkwinkel um der Linie zu folgen
    def get_streering_angle(self, frame, mode='light'):
        cropped_frame, offset = self.__crop_frame(frame)
        cropped_frame = cv2.GaussianBlur(cropped_frame, (5,5), 0)
        cropped_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("debug", cropped_frame)
        #Modus zum Folgen einer hellen oder dunklen Linie
        if mode == 'dark':
            ret, mask = cv2.threshold(cropped_frame, self.threshold_dark, 255, cv2.THRESH_BINARY_INV)
        else:
            ret, mask = cv2.threshold(cropped_frame, self.threshold_light, 255, cv2.THRESH_BINARY)

        cv2.imshow("mask", mask)
        # mask = cv2.inRange(cropped_frame, self.high_b, self.low_b)
        #ermittelt die Kontrastkonturen im Bild
        contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0 :
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] !=0 :
                #setzt die Werte wo sich der Mittelpunkt der Linie befindet
                self.cx = int(M['m10']/M['m00'])
                self.cy = int(M['m01']/M['m00']) + offset
                # print("CX : "+str(cx)+"  CY : "+str(cy))

                frame_height, frame_width, _ = frame.shape
                # 0 = mitte des bildes
                relative_position = self.cx / (frame_width / 2) -1

            #setzt den Lenkwinkel
                self.steering_angle = int(self.lenkangschlag * relative_position)
                
                # print("Steering angle:", self.steering_angle)

                cv2.drawContours(frame, c+(0, int(frame_height * self.crop_factor)), -1,(0,255,0), 1)
            
        
        
        return self.steering_angle
        #zeichnet die Linien in das Videofenster auf dem PC
    def draw_annotations(self, frame):
        frame_height, frame_width, _ = frame.shape

        cv2.circle(frame,(self.cx,self.cy),5, (255,255,255), -1)
        cv2.line(frame, (self.cx,self.cy), (int(frame_width / 2), frame_height), color=(48, 22, 198), thickness=4)
        cv2.line(frame, (0, int(frame_height * self.crop_factor)), (frame_width, int(frame_height * self.crop_factor)), color=(170,170,170), thickness=2)