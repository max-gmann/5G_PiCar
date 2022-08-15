import requests
import logging
import cv2
from multiprocessing.dummy import Pool
import asyncio
import socket

class pi_car:
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
    cali_ok = {"action": "camcaliok"}
    cam_up = {"action": "camcaliup"}
    cam_down = {"action": "camcalidown"}
    cam_left = {"action": "camcalileft"}
    cam_right = {"action": "camcaliright"}

    def __init__(self, default_speed=30, 
                default_camera_turn_angle_lr = 40, # left right
                default_camera_turn_angle_ud = 20):# up down

        self.dns_name = "raspberrypi"
        self.ip_adress = socket.gethostbyname(self.dns_name)
        self.base_url = "http://" + self.ip_adress
        self.control_url = self.base_url + ":8000/run/"
        self.calibration_url = self.base_url + ":8000/cali/"
        self.video_url = self.base_url + ":8765/mjpg"
        
        self.loop = asyncio.get_event_loop()
        self.session = requests.Session()
        self.__setup__()

        self.stopped = True
        self.is_straight = True
        self.is_left = False
        self.is_right = False
        self.is_forward = False
        self.is_backward = False
        self.previous_angle = 0
        
        # set speed / default speed = 30 / 100
        self.speed = -1
        self.set_speed(default_speed)
        self.pool = Pool(1)

        # set angle to turn the camera
        self.camera_turn_angle_lr = default_camera_turn_angle_lr
        self.camera_turn_angle_ud = default_camera_turn_angle_ud

    def __enter__(self):
        logging.info("System Startup...")
        
        

        # import asyncio
        # import aiohttp
        # from aiohttp.client import ClientSession
        # self.connection = aiohttp.TCPConnector(limit=10)
        # self.session = async aiohttp.ClientSession(connector=self.connection)

        self.camera_straight()
        logging.info("Camera check complete.")

        self.ready()
        logging.info("Motor & Servo check complete.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info("Shutting down...")
        self.session.close()
        logging.info("Returning to ready state.")
        self.stop()
        self.ready()
        self.camera_straight()
        cv2.destroyAllWindows()
        logging.info("Bye Bye!")

    def __setup__(self):
        logging.info("Initializing Pi Car")
        self.session.get(self.control_url, params={"action": "setup"})

    # Movement Controls ###########################################

    # async def send_request(self, action, session):
    #     async with session.get(pi_car.control_url, action):
    #         pass

    def set_speed(self, speed):
        if self.speed != speed:
            self.session.get(self.control_url, params={"speed": speed})
            self.speed = speed
        return speed

    def ready(self):
        requests.get(self.control_url, pi_car.move_ready)
        logging.info("Ready")
    
    def forward(self):
        self.stopped = False
        self.is_backward = False
        if not self.is_forward:
            self.is_forward = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_forward])
            logging.info("Forward")
    
    def backward(self):
        self.stopped = False
        self.is_forward = False
        if not self.is_backward:
            self.is_backward = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_backward])
        logging.info("Backward")
    
    def stop(self):
        self.is_backward = False
        self.is_forward = False
        if not self.stopped:
            self.stopped = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_stop])
            logging.info("Stop")
    
    def straight(self):
        self.is_left = False
        self.is_right = False
        if not self.is_straight:
            self.is_straight = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_straight])
            logging.info("Straight")
    
    def left(self):
        self.is_straight = False
        self.is_right = False
        if not self.is_left:
            self.is_left = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_left])
            logging.info("Left")

    def right(self):
        self.is_left = False
        self.is_straight = False
        if not self.is_right:
            self.is_right = True
            self.pool.apply_async(requests.get, [self.control_url, pi_car.move_right])
            logging.info("Right")
    
    # 90 = straight
    def turn(self, turn_angle):
        self.is_straight = False
        self.is_left = False
        self.is_right = False
        if turn_angle != self.previous_angle: 
            self.pool.apply_async(requests.get, [self.control_url, {'action': 'fwturn:'+ str(turn_angle+90)}])
            self.previous_angle = turn_angle
            logging.info("turn " + str(turn_angle))
        # requests.get(self.control_url, {'action': 'fwturn:'+ str(turn_angle+90)})

    # Camera Controls (limited to calibration for now) ###########################################

    def camera_straight(self):
        requests.get(self.control_url, pi_car.cam_ready)
        logging.info("Camera straight")

    def camera_up(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(self.calibration_url, pi_car.cam_up)
        logging.info("Camera up")
    
    def camera_down(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(self.calibration_url, pi_car.cam_down)
        logging.info("Camera down")
    
    def camera_left(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(self.calibration_url, pi_car.cam_left)
        logging.info("Camera left")
    
    def camera_right(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(self.calibration_url, pi_car.cam_right)
        logging.info("Camera right")

    def camera_ok(self):
        requests.get(self.control_url, self.cali_ok)