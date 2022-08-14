import requests
import logging
import cv2
from multiprocessing.dummy import Pool
import asyncio

class pi_car:
    # Connection Settings
    base_url = "http://raspberrypi"
    control_url = base_url + ":8000/run/"
    video_url = base_url + ":8765/mjpg"

    # Pi Car Controls
    move_forward = {"action": "forward"}
    move_stop = {"action": "stop"}
    move_backward = {"action": "backward"}
    move_left = {"action": "fwleft"}
    move_right = {"action": "fwright"}
    move_turn = {"action" : "fwturn:"}
    move_straight = {"action": "fwstraight"}
    move_ready = {"action": "fwready"}
    move_turn = {"action": "fwturn:"}

    # Camera Controls
    cam_ready = {"action": "camready"}
    cam_up = {"action": "camup"}
    cam_down = {"action": "camdown"}
    cam_left = {"action": "camleft"}
    cam_right = {"action": "camright"}

    def __init__(self, default_speed=30, 
                default_camera_turn_angle_lr = 40, # left right
                default_camera_turn_angle_ud = 20):# up down
        self.loop = asyncio.get_event_loop()

        self.__setup__()

        self.stopped = True
        self.is_straight = True
        self.is_left = False
        self.is_right = False
        self.is_forward = False
        self.is_backward = False
        
        # set speed / default speed = 30 / 100
        self.speed = self.set_speed(default_speed)
        self.pool = Pool(1)

        # set angle to turn the camera
        self.camera_turn_angle_lr = default_camera_turn_angle_lr
        self.camera_turn_angle_ud = default_camera_turn_angle_ud

    def __enter__(self):
        logging.info("System Startup...")

        self.camera_straight()
        logging.info("Camera check complete.")

        self.ready()
        logging.info("Motor & Servo check complete.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info("Shutting down...")
        logging.info("Returning to ready state.")
        self.stop()
        self.ready()
        self.camera_straight()
        cv2.destroyAllWindows()
        logging.info("Bye Bye!")

    def __setup__(self):
        logging.info("Initializing Pi Car")
        requests.get(self.control_url, {"action": "setup"})

    # Movement Controls ###########################################

    def set_speed(self, speed):
        requests.get(pi_car.control_url, {"speed": speed})
        return speed

    def ready(self):
        requests.get(pi_car.control_url, pi_car.move_ready)
        logging.info("Ready")
    
    def forward(self):
        self.stopped = False
        if not self.is_forward:
            self.is_forward = True
            self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_forward])
        # requests.get(pi_car.control_url, pi_car.move_forward)
            logging.info("Forward")
    
    def backward(self):
        self.stopped = False
        if not self.is_backward:
            self.is_backward = True
            self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_backward])
        # requests.get(pi_car.control_url, pi_car.move_backward)
        logging.info("Backward")
    
    def stop(self):
        self.is_backward = False
        self.is_forward = False
        if not self.stopped:
            self.stopped = True
            self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_stop])
        # requests.get(pi_car.control_url, pi_car.move_stop)
            logging.info("Stop")
    
    def straight(self):
        self.is_left = False
        self.is_right = False
        if not self.is_straight:
            self.is_straight = True
            self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_straight])
        # requests.get(pi_car.control_url, pi_car.move_straight)
            logging.info("Straight")
    
    def left(self):
        self.is_straight = False
        self.is_right = False
        if not self.is_left:
            self.is_left = True
            requests.get(pi_car.control_url, pi_car.move_left)
            # self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_left])
            logging.info("Left")

    def right(self):
        self.is_left = False
        self.is_straight = False
        if not self.is_right:
            self.is_right = True
            # self.pool.apply_async(requests.get, [pi_car.control_url, pi_car.move_right])
            requests.get(pi_car.control_url, pi_car.move_right)
            logging.info("Right")
    
    # 90 = straight
    def turn(self, turn_angle):
        self.is_straight = False
        requests.get(pi_car.control_url, {'action': 'fwturn:'+ str(turn_angle+90)})
        # try:
        #     self.pool.apply_async(requests.get, [pi_car.control_url, {'action': 'fwturn:'+ str(turn_angle+90)}])
        # except:
        #     pass
        logging.info("turn " + str(turn_angle))

    # Camera Controls ###########################################

    def camera_straight(self):
        requests.get(pi_car.control_url, pi_car.cam_ready)
        logging.info("Camera straight")

    def camera_up(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(pi_car.control_url, pi_car.cam_up)
        logging.info("Camera up")
    
    def camera_down(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(pi_car.control_url, pi_car.cam_down)
        logging.info("Camera down")
    
    def camera_left(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(pi_car.control_url, pi_car.cam_left)
        logging.info("Camera left")
    
    def camera_right(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(pi_car.control_url, pi_car.cam_right)
        logging.info("Camera right")