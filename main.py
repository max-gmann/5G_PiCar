import logging, time
import cv2
import keyboard

from Pi_Car_Controls import pi_car
from Streaming_Controls import video_player, video_streamer
from Object_Detector import stop_sign, person
from LineFollower import LineFollower
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class Mode:
    def __init__(self) -> None:
        pass

    def set_mode(self, mode):
        self.mode = mode 


with pi_car(default_speed=30) as car:

    mode = Mode.instance()
    mode.set_mode(True)

    streamer = video_streamer(streaming_url = car.video_url)
    streamer.start()

    player = video_player(fps_limit = 25)

    stop_sign_detector = stop_sign()
    person_detector = person()

    line_follower = LineFollower()
    steering_update_freq = 4 # relative to framerate, can never exeed framerate
    steering_counter = 0

    forward = False
    
    def change_mode():
        mode = Mode.instance()
        if mode.mode:
            mode.mode = False
        else:
            mode.mode = True
    
    def nothing():
        pass

    keymapping = {
        "w": car.forward,
        "s": car.backward,
        "a": car.left,
        "d": car.right,
        "m": change_mode
    }
    
    reverse_keymapping = {
        "w": car.stop,
        "s": car.stop,
        "a": car.straight,
        "d": car.straight,
        "m": nothing
    }
    
    was_pressed = dict.fromkeys(keymapping.keys(), False)
    stoped = True

    def callback_fnc(key):
        print("callback")
        key_name = key.name
        event_type = key.event_type
        
        if key_name in keymapping.keys():
            if event_type == 'down':
                print("before")
                keymapping[key_name]()
                print("after")
            elif event_type == 'up':
                reverse_keymapping[key_name]()


    keyboard.hook(callback_fnc) 

    while True:
        
        frame = streamer.read()        
        player.update_frame(frame, fps=True)    # update player with current frame and add fps annotation (doesnt display it yet)

        if player.next():

            if not mode.mode:
                steering_counter += 1
                
                if steering_counter % steering_update_freq == 0:
                    steering_angle = line_follower.get_streering_angle(frame)
                    car.turn(steering_angle)
                    steering_counter = 0
                
                line_follower.draw_annotations(frame)

                stop_sign_detector.get_prediction(frame)
                control_output, stop_bbox, border_color, relative_size_stop = stop_sign_detector.analyse_image(frame)
                person_detector.prediction = stop_sign_detector.prediction
                person_bbox, relative_size_person = person_detector.analyse_image(frame)


                player.update_bboxes(bbox=stop_bbox, bbox_title="Stop-Sign", bbox_subtitle=relative_size_stop)
                player.update_bboxes(bbox=person_bbox, bbox_title="Person", bbox_subtitle=relative_size_person, color = (100,100,100))
                player.update_border(border_color)
            else:
                
                # car.straight()
                # car.stop()

                # is_pressed = {key: keyboard.is_pressed(key) for (key, value) in keymapping.items()}  # get which keys are currently pressed
                
                # if all(value == False for value in is_pressed.values()) and stoped == False:
                #     car.stop()
                #     stoped = True
                #     print("Stop loop")
                #     pass
                # if not is_pressed['a'] and not is_pressed['d']:
                #     print("straight loop")
                #     # car.straight()
                #     pass
                # for key in keymapping.keys():
                #     if is_pressed[key] and not was_pressed[key]:
                #         # onyl run commands for new keys
                #         print(key)
                #         stoped = False
                #         keymapping[key]()
                    
                        
                # was_pressed = is_pressed
                
                pass
            player.show()
        
        

        if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
            player.close()
            streamer.close()
            break



