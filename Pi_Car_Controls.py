import requests#
import logging

class pi_car:
    # Connection Settings
    base_url = "http://192.168.0.168"
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
        # set speed / default speed = 30 / 100
        self.speed = self.set_speed(default_speed)

        # set angle to turn the camera
        self.camera_turn_angle_lr = default_camera_turn_angle_lr
        self.camera_turn_angle_ud = default_camera_turn_angle_ud

    def __enter__(self):
        logging.debug("Performing System Check...")
        
        self.camera_left()
        self.camera_straight()
        self.camera_right()
        self.camera_straight()
        self.camera_up()
        self.camera_straight()
        self.camera_down()
        self.camera_straight()
        logging.info("Camera check complete.")

        self.left()
        self.ready()
        self.right()
        self.turn()
        self.ready()
        self.forward()
        self.backward()
        self.stop()
        logging.info("Motor & Servo check complete.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.ready()
        self.camera_straight()
        logging.info("Returning to ready state.")
        logging.debug("Bye Bye")

        
    # Movement Controls ###########################################

    def set_speed(self, speed):
        requests.get(pi_car.control_url, {"speed": speed})
        return speed

    def ready(self):
        requests.get(pi_car.control_url, pi_car.move_ready)
        logging.debug("Ready")
    
    def forward(self):
        requests.get(pi_car.control_url, pi_car.move_forward)
        logging.debug("Forward")
    
    def backward(self):
        requests.get(pi_car.control_url, pi_car.move_backward)
        logging.debug("Backward")
    
    def stop(self):
        requests.get(pi_car.control_url, pi_car.move_stop)
        logging.debug("Stop")
    
    def straight(self):
        requests.get(pi_car.control_url, pi_car.move_straight)
        logging.debug("Straight")
    
    def left(self):
        requests.get(pi_car.control_url, pi_car.move_left)
        logging.debug("Left")
    
    def turn(self, turn_angle):
        requests.get(pi_car.control_url, {'action': 'fwturn:'+ str(turn_angle)})
        logging.debug(f"Turning {turn_angle}")

    def right(self):
        requests.get(pi_car.control_url, pi_car.move_right)
        logging.debug("Right")

    def turn(self, turn_angle):
        requests.get(pi_car.control_url, {'action': 'fwturn:'+ str(turn_angle+90)})
        logging.debug("turn " + str(turn_angle))

    # Camera Controls ###########################################

    def camera_straight(self):
        requests.get(pi_car.control_url, pi_car.cam_ready)
        logging.debug("Camera straight")

    def camera_up(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(pi_car.control_url, pi_car.cam_up)
        logging.debug("Camera up")
    
    def camera_down(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_ud
        requests.get(pi_car.control_url, pi_car.cam_down)
        logging.debug("Camera down")
    
    def camera_left(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(pi_car.control_url, pi_car.cam_left)
        logging.debug("Camera left")
    
    def camera_right(self, turn_angle = -1):
        if turn_angle == -1:
            turn_angle = self.camera_turn_angle_lr
        requests.get(pi_car.control_url, pi_car.cam_right)
        logging.debug("Camera right")