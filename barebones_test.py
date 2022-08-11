from tracemalloc import stop
from Pi_Car_Controls import pi_car
from Streaming_Controls import video_player, video_streamer
import logging, time
logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)
import cv2
from Object_Detector import stop_sign, person
from LineFollower import LineFollower

with pi_car(default_speed=30) as car:

    streamer = video_streamer(streaming_url = car.video_url)
    streamer.start()

    player = video_player(fps_limit = 25)

    stop_sign_detector = stop_sign()
    person_detector = person()

    line_follower = LineFollower()
    steering_update_freq = 4 # relative to framerate, can never exeed framerate
    steering_counter = 0
    while True:
        
        frame = streamer.read()        
        player.update_frame(frame, fps=True)

        if player.next():
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