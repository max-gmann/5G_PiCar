import time
from util.Singleton import Singleton
import logging

# this decorator means there can only ever be one mode
# object at a time that can also be accessed anywhere
@Singleton  
class Mode:
    def __init__(self) -> None:
        self.is_5g = True
        
        self.manual_mode = True
        self.line_follow = False
        self.stop_detection = False   
        
        self.auto_run = True    
        self.line_color_dark = True

    def toggle_autonomy_mode(self):
        if self.manual_mode:
            logging.info("Disabling manual mode in 3.")
            time.sleep(1)
            logging.info("Disabling manual mode in 2.")
            time.sleep(1)
            logging.info("Disabling manual mode in 1.")
            time.sleep(1)
        else:
            logging.info("Enabling manual mode.")
        self.manual_mode = not self.manual_mode
        self.toggle_line_following()
        self.toggle_stop_detection()
        
    def toggle_connection_mode(self):
        logging.info("Switching connection mode.")
        self.is_5g = not self.is_5g    

    def toggle_line_following(self):
        self.line_follow = not self.line_follow    

    def toggle_stop_detection(self):
        self.stop_detection = not self.stop_detection    

    def toggle_auto_run(self):
        logging.info("Toggling auto run.")
        self.auto_run = not self.auto_run    
    
    def toggle_line_color(self):
        logging.info("Toggling line color to follow.")
        self.line_color_dark = not self.line_color_dark