import os
import time
import sys
# comment out below line to enable tensorflow outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from core.functions import *
from polytrack.track import track
from polytrack.bg_subtraction import foreground_changes
from polytrack.record import record_track, complete_tracking
from polytrack.config import pt_cfg
from polytrack.flowers import record_flowers
from polytrack.general import *
import cv2
import numpy as np
# import warnings; warnings.simplefilter('ignore')
from datetime import datetime
from absl import app


def main(_argv):
    start_time = datetime.now()
    start_time_py = time.time()
    print("Start:  " + str(start_time))
    nframe = 0
    # total_frames = 0
    # flowers_recorded = False
    # predicted_position =[]

    video_list = get_video_list(pt_cfg.POLYTRACK.INPUT_DIR, pt_cfg.POLYTRACK.VIDEO_EXT)

    for video_name in video_list:
        
        print('===================' + str(video_name) + '===================')

        video = str(pt_cfg.POLYTRACK.INPUT_DIR) + str(video_name)

        # begin video capture
        try:
            vid = cv2.VideoCapture(int(video))
        except:
            vid = cv2.VideoCapture(video)

        
        width, height, _ = get_video_details(vid)
        converter = cv2.VideoWriter(str(pt_cfg.POLYTRACK.OUTPUT)+str(video_name)+'.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, (width, height))
        
        while True:
            return_value, frame = vid.read()
            if return_value:
                nframe += 1

                
               # cv2.imshow("frame", frame)
                converter.write(frame)

                # idle = check_idle(nframe, predicted_position)
                # insectsBS =  foreground_changes(frame, width, height, nframe, idle)
                # associated_det_BS, associated_det_DL, missing,new_insect = track(frame, predicted_position, insectsBS)
                # for_predictions = record_track(frame, nframe,associated_det_BS, associated_det_DL, missing, new_insect, idle)
                # predicted_position = predict_next(for_predictions)

                fps = round(nframe/ (time.time() - start_time_py),2)
                print(str(nframe) + ' frames processed | ' + str(fps) +' FPS     ' , end='\r')


                if cv2.waitKey(1) & 0xFF == ord('q'): break
                
            else:
                print()
                print('Video has ended')
                break

        if not pt_cfg.POLYTRACK.CONTINUOUS_VIDEO:
            pass
            # complete_tracking(predicted_position)
            # predicted_position =[]
            # pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS = []
            # flowers_recorded = False
        

    cv2.destroyAllWindows()
    complete_tracking(predicted_position)
    end_time = datetime.now()
    print()
    print("End:  " + str(end_time))
    print("Processing Time:  " + str(end_time-start_time))





if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass

