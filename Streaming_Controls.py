import cv2
import time
import logging
# logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)
from threading import Thread
import numpy as np

from util.Operating_Mode import Mode

class video_streamer():
    WIDTH = 640
    HEIGHT = 480
    
    default_window_title = "Pi Car Demo"

    fps_counter_position = (20, 460)

    font                   = cv2.FONT_HERSHEY_SIMPLEX
    fontScale              = 0.8
    fontColor              = (255,255,255)
    thickness              = 1
    lineType               = 2

    bordersize = 10
    default_border_color = [255, 0, 0]

    def __init__(self, 
                streaming_url = 0):

        self.streaming_url = streaming_url

        self.is_5g = Mode.instance().get_connection_mode
        self.delay_frames_4g = 5
        self.frame_buffer = []
        self.buffer_size = 50
        
        self.__set_capture()

        # thread initialization
        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def update(self):
        logging.info("Streaming started.")
        connection_changed = False
        while True:
            if self.stopped is True:
                break
            self.get_image()

            if self.grabbed is False:
                logging.warning("No frames to read. Exiting...")
                self.stopped = True
                break
        
        logging.info("Streaming ended.")
        self.cap.release()
    
    def read(self):
        if self.is_5g():
            return self.frame_buffer[-1]
        else:
            return self.frame_buffer[-self.delay_frames_4g]

    def stop(self):
        self.stopped = True

    # Initializes the capture if webcam is used for debugging
    def __set_capture(self):
        self.cap = cv2.VideoCapture(self.streaming_url)
        if self.cap.isOpened() is False:
            logging.warning("Error accessing video stream. Exiting...")
            exit(0)

        fps_input_stream = self.cap.get(5) # hardware fps
        width, height = self.cap.get(3), self.cap.get(4)
        logging.info(f"Camera Hardware Info: {width} x {height} @ {fps_input_stream}")

        self.cap.set(3,video_streamer.WIDTH) 
        self.cap.set(4,video_streamer.HEIGHT) 

        logging.info(f"Streaming Resolution: {self.WIDTH} x {self.HEIGHT} @ {fps_input_stream}")

        # reading initial frame for initialization
        self.grabbed, self.last_frame = self.cap.read()
        self.frame_buffer.append(self.last_frame)

        if self.grabbed is False:
            logging.warning("No frames to read. Exiting...")
            exit(0)

    # closes the capture and shuts everything down
    def close(self):
        logging.info("Shutting down streamer.")
        self.stop()
        self.cap.release()
    
    # returns a new image
    def get_image(self):
        try:
                self.grabbed, self.last_frame = self.cap.read()
                self.frame_buffer.append(self.last_frame)
                if len(self.frame_buffer) >= self.buffer_size:
                    self.frame_buffer.pop(0)
        except Exception as e:
            logging.warning("Couldnt capture or read video stream.")
            logging.warning(e.with_traceback)

        return self.last_frame
    
class fps_counter():
    def __init__(self, fps_limit, print_logging=True) -> None:
        self.fps_limit = fps_limit
        self.print_logging = print_logging
        self.prev = 0
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.fps = 0
        self.logging_counter = 1

    def next(self):
        time_elapsed = time.time() - self.prev
        if time_elapsed > 1./self.fps_limit:
            self.prev = time.time()

            # Measure FPS
            self.new_frame_time = time.time()
            self.fps = 1/(self.new_frame_time-self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
            self.fps = int(self.fps) + 1

            if self.print_logging and self.logging_counter % self.fps_limit == 0:
                logging.info(f"FPS: {self.fps}")
                self.logging_counter = 1
            else:
                self.logging_counter += 1

            return True
        else:
            return False

    def get_fps(self):
        return self.fps

class video_player():

    def __init__(self, 
                fps_limit = 25,
                title="Pi Car Demo"):

        logging.info("Starting Video Player.")
        self.fps_limit = fps_limit
        self.scheduler = fps_counter(fps_limit)
        self.input_frame = None

        self.window_title = title

        self.relative_size_text = ""
        self.color = (100, 100, 100)
    
    def print_text(self, text, position=(600, 470), color= (0,0,0), size=0.4):
        cv2.putText(self.output_image, text, position,
            video_streamer.font, 
            size,
            color,
            1,
            video_streamer.lineType)

    def update_frame(self, image, fps=True):
        self.output_image = image
        if fps:
            self.get_fps_overlay()

    def update_bboxes(self, bbox, bbox_title = "", bbox_subtitle = "", color = None):
        if color is None:
            color = self.color
        self.bboxes = bbox
        if bbox is not None:
            self.draw_prediction(bbox_title, bbox_subtitle, color) 

    def update_border(self, color):
        self.color = color
        self.get_border_overlay()

    def show(self):
        cv2.imshow(self.window_title, self.output_image)
        self.output_image = None

    def next(self):
        return self.scheduler.next()
    
    def close(self):
        logging.info("Closing Video Player.")
        cv2.destroyAllWindows()
        cv2.waitKey(1)      

    def draw_prediction(self, title, subtitle, color):
        box = self.bboxes
        cv2.rectangle(
            self.output_image,
            (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), 
            color, 
            2)

        cv2.putText(self.output_image, title, (int(box[0]), int(box[1]-8)),
            video_streamer.font, 
            0.4,
            color,
            1,
            video_streamer.lineType)
        
        cv2.putText(self.output_image, f"{str(subtitle)}", (int(box[0]), int(box[3]+ 10)),
            video_streamer.font, 
            0.4,
            color,
            1,
            video_streamer.lineType)
        

    # adds the fps counter to the image
    def get_fps_overlay(self):
        self.output_image = cv2.putText(self.output_image, "FPS: " + str(self.scheduler.get_fps()), video_streamer.fps_counter_position, 
        video_streamer.font, 
        video_streamer.fontScale,
        video_streamer.fontColor,
        video_streamer.thickness,
        video_streamer.lineType)
    
    # adds a border overlay to the image
    def get_border_overlay(self):
        bordersize = video_streamer.bordersize 
        self.output_image = cv2.copyMakeBorder(
            self.output_image,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=self.color
        ) 