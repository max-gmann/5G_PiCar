import torch, cv2, time
from abc import abstractclassmethod
import logging



class obstacle():
    def __init__(self, name):
        self.name = name
        self.num_instances = 0
        self.bboxes = None
        self.__build_yolo_model()
        self.relative_size = None

    def __build_yolo_model(self):
        self.predictor = torch.hub.load('ultralytics/yolov5', 'yolov5n')

    @abstractclassmethod
    def analyse_image(self, image):
        pass

    @abstractclassmethod
    def __get_control_output():
        pass

    def get_prediction(self, image):
        self.prediction = self.predictor(image)
        return self.prediction

    

class person(obstacle):
    def __init__(self):
        super().__init__("person")
        self.label = "person"

    def analyse_image(self, img):
        self.image = img
        self.num_instances = 0

        for instance in self.prediction.xyxy:
            if len(instance.tolist()) != 0:
                label =  self.prediction.names[int(instance.tolist()[0][-1])]
                if label == self.label:
                    self.bboxes = instance.tolist()[0][:4]
                    self.num_instances += 1
        
        if self.num_instances == 0:
            self.bboxes = None
            self.num_instances = 0
        
        self.__get_relative_size()
        
        return self.bboxes, self.relative_size

    def __get_relative_size(self):
        if self.bboxes is not None:
            box = self.bboxes
            width = max(box[1], box[3]) - min(box[1], box[3])
            
            img_width = self.image.shape[1]
            self.relative_size = round((width / img_width), 2)
        else:
            self.relative_size = 0.0

class stop_sign(obstacle):

    RELATIVE_SIZE_TO_STOP = 0.1

    FRAMES_TO_CONFIRM_START = 12
    FRAMES_TO_CONFIRM_END = 50
    WAIT_TIME = 4.0

    def __init__(self):
        super().__init__("stop_sign")

        self.frames_seen = 0
        self.frames_not_seen = 0
        self.relative_size = None
        self.active = 0
        self.released = True
        self.wait_timer_start = None
    

    def __detect_stop_signs(self):
        self.num_instances = 0

        for instance in self.prediction.xyxy:
            if len(instance.tolist()) != 0:
                label =  self.prediction.names[int(instance.tolist()[0][-1])]
                if label == "stop sign":
                    self.bboxes = instance.tolist()[0][:4]
                    self.num_instances += 1
        
        if self.num_instances == 0:
            self.bboxes = None
            self.num_instances = 0

    def analyse_image(self, img, model_input_size = (640, 480)):
        
        # resize image
        # img = cv2.resize(img, model_input_size, interpolation = cv2.INTER_AREA)

        self.image = img

        self.__detect_stop_signs()

        if self.num_instances > 0:
            if self.active and self.released:
                pass
            else:
                self.__get_relative_size()
                if self.relative_size >= stop_sign.RELATIVE_SIZE_TO_STOP:
                    self.frames_seen += 1

                    if self.frames_seen > stop_sign.FRAMES_TO_CONFIRM_START:
                        self.active = True
                        self.__start_wait()

        elif self.active:
            self.frames_not_seen += 1
            if self.frames_not_seen > stop_sign.FRAMES_TO_CONFIRM_END:
                logging.info("Stopsign deactivated.")
                self.active = False
                self.frames_not_seen = 0
                self.frames_seen = 0

        return self.__get_control_output(), self.bboxes, self.__get_color_code(), self.relative_size

    def __get_color_code(self):
        if self.active and not self.released:
            return (0, 0, 255) # red
        if self.active and self.released:
            return (255, 0, 0) # blue
            #return (220, 208, 255) # lilac
        if self.released:
            return (0, 255, 0) # green

    def __get_control_output(self):
        now = time.time()
        if self.wait_timer_start is None:
            return "go"

        if (now - self.wait_timer_start) >= stop_sign.WAIT_TIME:
            logging.info("Released.")
            self.released = True
            self.wait_timer_start = None
            
        if self.released is True:
            return "go"
        else:
            return "stop"        

    def __start_wait(self):
        if self.wait_timer_start is None:
            logging.info("Stopsign active. Starting timer.")
            self.wait_timer_start = time.time()
            self.released = False

    def __get_relative_size(self):
        if self.bboxes is not None:
            box = self.bboxes
            height = max(box[0], box[2]) - min(box[0], box[2])
            
            img_height = self.image.shape[0]
            self.relative_size = round((height / img_height), 2)
        else:
            self.relative_size = 0.0