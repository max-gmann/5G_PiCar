import cv2
import time
import logging
logging.basicConfig(format='[%(asctime)s | Streaming_Controls | %(levelname)s] - %(message)s', level=logging.DEBUG)


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
                streaming_url = 0, 
                fps_limit = 24, 
                overlays=['fps', 'size', 'border', 'bbox']):

        self.streaming_url = streaming_url
        self.overlays = overlays
        self.border_color = video_streamer.default_border_color
        self.fps_limit = fps_limit
        self.scheduler = fps_counter(fps_limit)
        self.__set_capture()

    # Initializes the capture if webcam is used for debugging
    def __set_capture(self):
        if self.streaming_url != 0:
            self.cap = None
        else:
            self.cap = cv2.VideoCapture(self.streaming_url)
            self.cap.set(3,video_streamer.WIDTH) 
            self.cap.set(4,video_streamer.HEIGHT) 

    # returns true if new image is available
    def next(self):
        return self.scheduler.next()

    # closes the capture and shuts everything down
    def close(self):
        logging.debug("Shutting down streamer.")
        cv2.destroyAllWindows() 
        cv2.waitKey(1)
        if self.streaming_url == 0:
            self.cap.release()
    
    # returns a new image
    def get_image(self):
        try:
            if self.streaming_url != 0:
                self.cap = cv2.VideoCapture(self.streaming_url)
            success, img = self.cap.read()
            self.last_frame = img
        except Exception as e:
            logging.warning("Couldnt capture or read video stream.")
            logging.warning(e.with_traceback)
            img = None
        finally:
            if self.streaming_url != 0:
                self.cap.release()

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

        return output_img
    
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
    def __init__(self, fps_limit) -> None:
        self.fps_limit = fps_limit
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
            logging.debug(f"FPS: {self.fps}")
            return True
        else:
            return False

    def get_fps(self):
        return self.fps