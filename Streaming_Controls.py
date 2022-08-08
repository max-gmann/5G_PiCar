import cv2
import time
import logging
from threading import Thread

class video_streamer():
    WIDTH = 1280
    HEIGHT = 720
    
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
                streaming_url = 0, 
<<<<<<< HEAD
                fps_limit = 24, 
                print_logging = True,
=======
                fps_limit = 30, 
>>>>>>> 7e3bf2f83fc3f2aa0ce566a2e3660b761da84d32
                overlays=['fps', 'size', 'border', 'bbox']):

        self.streaming_url = streaming_url
        self.overlays = overlays
        self.print_logging = print_logging
        self.border_color = video_streamer.default_border_color
        self.fps_limit = fps_limit
        self.scheduler = fps_counter(fps_limit, self.print_logging)
        self.__set_capture()

        # thread initialization
        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def update(self):
        while True:
            if self.stopped is True:
                break
            self.get_image()
            if self.grabbed is False:
                logging.warning("No frames to read. Exiting...")
                self.stopped = True
                break

        self.cap.release()
    
    def read(self):
        return self.last_frame

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
        logging.info(f"Hardware FPS: {fps_input_stream} @ {width}x{height}")
        
        self.cap.set(3,video_streamer.WIDTH) 
        self.cap.set(4,video_streamer.HEIGHT) 

        # reading initial frame for initialization
        self.grabbed, self.last_frame = self.cap.read()

        if self.grabbed is False:
            logging.warning("No frames to read. Exiting...")
            exit(0)

        # if self.streaming_url != 0:
        #     self.cap.release()
        #     self.cap = None

    # returns true if new frame is scheduled according to fps limit
    def next(self):
        return self.scheduler.next()

    # closes the capture and shuts everything down
    def close(self):
        logging.debug("Shutting down streamer.")
        self.stop()
        cv2.destroyAllWindows() 
        cv2.waitKey(1)
        if self.streaming_url == 0:
            self.cap.release()
    
    # returns a new image
    def get_image(self):
        try:
            # if self.streaming_url != 0:
            #     self.cap = cv2.VideoCapture(self.streaming_url)
            self.grabbed, self.last_frame = self.cap.read()
        except Exception as e:
            logging.warning("Couldnt capture or read video stream.")
            logging.warning(e.with_traceback)
        # finally:
        #     if self.streaming_url != 0:
        #         self.cap.release()

        return self.last_frame

    # displays an image either provided to the function or it retrieves a new one
    def show(self, img=None, window_title=None, overlay=True, simple=False):
        # Output Image
        if img is not None:
            output_img = img
        else:
            if simple:
                self.get_image()
            output_img = self.last_frame
        
        # Window Title
        # Note: openCV overwrites windows with the same
        # title (useful for videos). Changing the window name
        # will create a new window.
        if not window_title:
            window_title = video_streamer.default_window_title
        
        # Add overlay text
        if overlay:
            output_img = self.add_overlay(output_img)

        # Show image with openCV
        cv2.imshow(window_title, output_img)

    
    # adds the overlays specified in the constructor
    def add_overlay(self, img):
        img = img.copy()
        if 'border' in self.overlays:
            img = self.get_border_overlay(img)

        if 'fps' in self.overlays:
            img = self.get_fps_overlay(img)

        if 'bbox' in self.overlays:
            pass
        
        if 'size' in self.overlays:
            pass

        return img

    # adds the fps counter to the image
    def get_fps_overlay(self, img):
        return cv2.putText(img, "FPS: " + str(self.scheduler.get_fps()), video_streamer.fps_counter_position, 
        video_streamer.font, 
        video_streamer.fontScale,
        video_streamer.fontColor,
        video_streamer.thickness,
        video_streamer.lineType)
    
    # setter for changing the border color according to vehicle actions (stoping, forward, etc)
    def set_border_color(self, color):
        self.border_color = color

    # adds a border overlay to the image
    def get_border_overlay(self, img):
        bordersize = video_streamer.bordersize 
        return cv2.copyMakeBorder(
            img,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=self.border_color
        ) 

class fps_counter():
    def __init__(self, fps_limit, print_logging=True) -> None:
        self.fps_limit = fps_limit
        self.print_logging = print_logging
        self.prev = 0
        self.prev_frame_time = 0
        self.new_frame_time = 0

    def next(self):
        time_elapsed = time.time() - self.prev
        if time_elapsed > 1./self.fps_limit:
            self.prev = time.time()

            # Measure FPS
            self.new_frame_time = time.time()
            self.fps = 1/(self.new_frame_time-self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
            self.fps = int(self.fps) + 1
            if self.print_logging:
                logging.debug(f"FPS: {self.fps}")
            return True
        else:
            return False

    def get_fps(self):
        return self.fps

class video_player():

    def __init__(self, image):

        self.input_img = image
        self.last_frame = None
        self.v = None

        self.relative_size_text = None
        self.color = (100, 100, 100)

        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def stop(self):
        self.stopped = True

    def read(self):
        if self.last_frame is None:
            return self.input_img
        else:
            return self.last_frame

    def update(self):
        while True:
            if self.stopped is True:
                break
            if self.input_img is not None:

                self.draw_prediction()
                
                self.streamer.show(self.read())

                if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
                    self.stop()
                    break
    
    def update_img(self, img, bboxes):
        self.input_img = img
        self.bboxes = bboxes

    def show_relative_size(self, text):
        self.relative_size_text = text

    def set_color(self, color):
        self.color = color

    def draw_prediction(self):
        #bboxes = self.prediction['instances'].pred_boxes.to('cpu').tensor.numpy()
    
        num_instances = len(self.bboxes)
        if num_instances > 0:
            if num_instances > 1:
                #scores = self.prediction['instances'].scores.tolist()
                #index_highest_prob = scores.index(max(scores))
                index_highest_prob = 0
            else:
                index_highest_prob = 0

            box = self.bboxes
            input = self.input_img.copy()
            self.last_frame = cv2.rectangle(
                input,
                (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), 
                self.color, 
                2)

            self.last_frame = cv2.putText(self.last_frame, "Stop-Sign", (int(box[0]), int(box[1]-8)),
                video_streamer.font, 
                0.4,
                self.color,
                1,
                video_streamer.lineType)
            
            if self.show_relative_size is not None:
                self.last_frame = cv2.putText(self.last_frame, f"{self.relative_size_text}", (int(box[0]), int(box[3]+ 10)),
                video_streamer.font, 
                0.4,
                self.color,
                1,
                video_streamer.lineType)
        else:
            self.last_frame = self.input_img
        