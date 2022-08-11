import cv2
import numpy as np

class LineFollower():
    def __init__(self) -> None:
        self.low_b = np.uint8([60,60,60])
        self.high_b = np.uint8([0,0,0])

    def get_streering_angle(self, frame):
        mask = cv2.inRange(frame, self.high_b, self.low_b)
        contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
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
            #     cv2.circle(frame,(cx,cy),5, (255,255,255), -1)
            # cv2.drawContours(frame, c, -1,(0,255,0), 1)
