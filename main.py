import logging, time, sys
import numpy as np
import cv2
import keyboard

# custom imports
from util.Operating_Mode import Mode
from Line_Follower import LineFollower
from Pi_Car_Controls import pi_car
from Streaming_Controls import video_player, video_streamer
from Object_Detector import stop_sign, person

# Logging setup
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)


def main():
    # instantiate pi car instance with default speed
    # the "with" statement means that some code will
    # be executed when the object is no longer needed
    # or something crashes. This should make sure to 
    # stop any commands and make the car stop.

    with pi_car(default_speed=30) as car:

        mode = Mode.instance()

        # Threaded streaming object for retrieving frames from pi car
        streamer = video_streamer(streaming_url = car.video_url)
        streamer.start()

        # video player object responsible for displaying and limiting
        # fps and drawing annotations
        player = video_player(fps_limit = 25)

        stop_sign_detector = stop_sign()
        person_detector = person()

        line_follower = LineFollower()
        steering_update_freq = 2 # relative to framerate, can never exeed framerate, every x frames
        steering_counter = 0
        control_output = "go"
        
        # placeholder function to do nothing
        # used when there is no need to execute a function 
        # when a key is depressed
        def nothing():
            pass

        # wird ausgeführt wenn eine Taste gedrückt wird
        keymapping = {
            "w": car.forward,
            "s": car.backward,
            "a": car.left,
            "d": car.right,
            "m": Mode.instance().toggle_autonomy_mode,
            "c": Mode.instance().toggle_connection_mode,  
            "f": Mode.instance().toggle_line_following,
            "p": Mode.instance().toggle_stop_detection,
            "nach-unten": car.camera_down,
            "nach-oben": car.camera_up,
            "nach-links": car.camera_left,
            "nach-rechts": car.camera_right,
            "space": Mode.instance().toggle_auto_run,
            'h': Mode.instance().toggle_line_color
        }
        
        # wird ausgeführt wenn eine Taste losgelassen wird
        reverse_keymapping = {
            "w": car.stop,
            "s": car.stop,
            "a": car.straight,
            "d": car.straight,
            "m": nothing,
            "c": nothing,
            "f": nothing,
            "p": nothing,
            "nach-unten": car.camera_ok,
            "nach-oben": car.camera_ok,
            "nach-links": car.camera_ok,
            "nach-rechts": car.camera_ok,
            "space": nothing,
            "h": nothing
        }
        
        # instantiate dict with boolean values for each key to 
        # track if a key was previously pressed 
        was_pressed = dict.fromkeys(keymapping.keys(), False)
        stoped = True

        # callback function called when a key is pressed
        def callback_fnc(key):
            key_name = key.name 
            event_type = key.event_type
            #setzt die Geschwidnigkeit des Autos
            if key_name in [str(number) for number in range(1,6,1)]:
                speed = str(int(key_name) * 10)
                car.set_speed(speed)
                logging.info(f"Setting speed to {str(int(key_name) * 10)}/50")
            #schaltet zwischen manueller Steuerung und Automatikmodus um
            elif key_name in keymapping.keys():
                if Mode.instance().manual_mode or key_name in ['c', 'm', 'f', 'p', 'space', 'h']:
                    if event_type == 'down':
                        keymapping[key_name]()
                    elif event_type == 'up':
                        reverse_keymapping[key_name]() 

        # register keyboard listener for manual controls
        keyboard.hook(callback_fnc) 

        # Hauptschleife
        while True:
            
            # liest die Bilder ein
            frame = streamer.read()        


            player.update_frame(frame, fps=True)     # update player with current frame and add fps annotation (doesnt display it yet)

            if player.next():
                if not mode.manual_mode:
                    steering_counter += 1
                    
                    # ruft die Stopschild und Personenerkennung auf
                    if mode.stop_detection:
                        stop_sign_detector.get_prediction(frame)
                        control_output, stop_bbox, border_color, relative_size_stop = stop_sign_detector.analyse_image(frame)
                        person_detector.prediction = stop_sign_detector.prediction
                        person_bbox, relative_size_person = person_detector.analyse_image(frame)
                    
                    # ruft die Linienerkennung auf und setzt den Lenkwinkel
                    if mode.line_follow:
                        if steering_counter % steering_update_freq == 0:
                            line_color = "dark" if mode.line_color_dark else "light"
                            steering_angle = line_follower.get_streering_angle(frame, line_color)
                            car.turn(steering_angle)
                            steering_counter = 0 
                    # zeichnet das Overlay ins Webcambild
                        line_follower.draw_annotations(frame)

                    if control_output == "go" and Mode.instance().auto_run:
                        car.forward()
                    else:
                        car.stop()

                    if mode.stop_detection:
                        player.update_bboxes(bbox=stop_bbox, bbox_title="Stop-Sign", bbox_subtitle=relative_size_stop)
                        player.update_bboxes(bbox=person_bbox, bbox_title="Person", bbox_subtitle=relative_size_person, color = (100,100,100))
                        player.update_border(border_color)
                else:
                    player.print_text("Manual Mode", (495, 460), (255,255,255), size= 0.6)

                # informiert ob es 4G oder 5G Modus ist
                if mode.is_5g:
                    player.print_text("5G", position=(15, 35),color=(0,255,0), size= 0.8)
                    player.print_text("Avg. Latency: [0, 40]ms", position=(15, 55),color=(0,255,0), size= 0.3)
                else:
                    player.print_text("4G", position=(15, 35),color=(0,0,255), size= 0.8)
                    player.print_text("Avg. Latency: [50, 250]ms", position=(15, 55),color=(0,0,255), size= 0.3)

                player.print_text(f"Speed: {car.speed}/50", position=(520, 25), color=(255,255,255), size=0.5)
                player.show()
            

            if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
                player.close()
                streamer.close()
                break


if __name__ == "__main__":
    print(sys.argv)
    main()