from tracemalloc import stop
from Pi_Car_Controls import pi_car
from Streaming_Controls import video_player, video_streamer
import logging, time
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)
import cv2
from Object_Detector import stop_sign, person

with pi_car(default_speed=30) as car:

    streamer = video_streamer(streaming_url = car.video_url)
    streamer.start()

    player = video_player(fps_limit = 25)

    stop_sign_detector = stop_sign()
    person_detector = person()

    while True:
        
        frame = streamer.read()        
        
        control_output, stop_bbox, border_color, relative_size = stop_sign_detector.analyse_image(frame)
        person_bbox = person_detector.analyse_image(frame)

        if player.next():
            player.update_frame(frame, fps=True)
            player.update_bboxes(bbox=stop_bbox, bbox_title="Stop-Sign", bbox_subtitle=relative_size)
            player.update_bboxes(bbox=person_bbox, bbox_title="Person", color = (100,100,100))
            player.update_border(border_color)
            player.show()
        
            

        if cv2.waitKey(1) & 0xFF==ord('q'): # quit when 'q' is pressed
            player.close()
            streamer.close()
            break

        # if player.stopped or streamer.stopped: # quit when 'q' is pressed
        #      streamer.close()
        #      player.stop()
        #      break

    # player = video_player(streamer.read())
    # player.start()

    # while True:
    #     if streamer.next():
    #         current_img = streamer.read()

    #         player.update_img(current_img)        

    #     if player.stopped or streamer.stopped: # quit when 'q' is pressed
    #         streamer.close()
    #         break