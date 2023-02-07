#from __future__ import print_function
import os
import time
import sys
# comment out below line to enable tensorflow outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from core.functions import *
from polytrack.track import track, prepare_to_track
from polytrack.bg_subtraction import foreground_changes
from polytrack.record import record_track, complete_tracking, setup_video_save
from polytrack.config import pt_cfg
from polytrack.flowers import record_flowers, track_flowers, save_flowers
from polytrack.general import *
import cv2
import numpy as np
# import warnings; warnings.simplefilter('ignore')
from datetime import datetime
from absl import app
from absl import app, flags, logging
from absl.flags import FLAGS

flags.DEFINE_string('input', pt_cfg.POLYTRACK.INPUT_DIR, 'path to input video directory')
flags.DEFINE_string('extension', pt_cfg.POLYTRACK.VIDEO_EXT, 'Video extension of the input video')
flags.DEFINE_string('output', pt_cfg.POLYTRACK.OUTPUT, 'path to output folder')
flags.DEFINE_boolean('show_video', pt_cfg.POLYTRACK.SHOW_VIDEO_OUTPUT, 'Show video output')
#flags.DEFINE_boolean('save_video', pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT, 'Save video output')

def main(_argv):
    start_time = datetime.now()
    start_time_py = time.time()
    print("Start:  " + str(start_time))
    nframe = 0
    total_frames = 0
    flowers_recorded = False
    predicted_position =[]
    idle = False
    pt_cfg.POLYTRACK.INPUT_DIR = FLAGS.input
    pt_cfg.POLYTRACK.OUTPUT = FLAGS.output
    pt_cfg.POLYTRACK.VIDEO_EXT = FLAGS.extension
    pt_cfg.POLYTRACK.SHOW_VIDEO_OUTPUT = FLAGS.show_video
    #pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT = FLAGS.save_video
    processing_text= open(str(pt_cfg.POLYTRACK.OUTPUT)+"video_details.txt","w+") #Print processing time to a file

    video_list = get_video_list(pt_cfg.POLYTRACK.INPUT_DIR, pt_cfg.POLYTRACK.VIDEO_EXT)

    for video_name in video_list:
        
        print('===================' + str(video_name) + '===================')

        video = str(pt_cfg.POLYTRACK.INPUT_DIR) + str(video_name)

        # begin video capture
        try:
            vid = cv2.VideoCapture(int(video))
        except:
            vid = cv2.VideoCapture(video)

        
        width, height, video_frames = get_video_details(vid)
        pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS = get_video_start_time(video_name, nframe)

        if not pt_cfg.POLYTRACK.VIDEO_OUTPUT_SETUP:setup_video_save(pt_cfg.POLYTRACK.OUTPUT)
        
        if pt_cfg.POLYTRACK.SIGHTING_TIMES: 
            try:
                pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS = get_video_start_time(video_name, nframe)
            except:
                print('Invalied filename format. Try renaming the file or setting the value of SIGHTING_TIMES to False in Configuration file')
                pt_cfg.POLYTRACK.SIGHTING_TIMES = False

        total_frames += video_frames
        video_start_frame = nframe
        
        #nframe = 14400
        #vid.set(1, nframe)
        #if idle: pt_cfg.POLYTRACK.INITIAL_FRAMES = video_start_frame + 150
        #if not flowers_recorded: flowers, flowers_recorded = record_flowers(vid, video_name)
        while True:
            return_value, frame = vid.read()
            if return_value:
                nframe += 1
                
                # if not flowers_recorded: flowers_recorded = record_flowers()
                if (nframe % pt_cfg.POLYTRACK.FLOWER_UPDATE_FREQUENCY == 60): track_flowers(nframe, frame) #60

                idle = check_idle(nframe, predicted_position)
                insectsBS =  foreground_changes(frame, width, height, nframe, idle)
                associated_det_BS, associated_det_DL, missing,new_insect = track(frame, predicted_position, insectsBS)
                #print(nframe, new_insect)
                nframe, idle, new_insect = prepare_to_track(nframe, vid, idle, new_insect, video_start_frame)
                for_predictions = record_track(frame, nframe,associated_det_BS, associated_det_DL, missing, new_insect, idle)
                predicted_position = predict_next(for_predictions)

                #print(nframe, len(insectsBS), new_insect, for_predictions)
                

                fps = round(nframe/ (time.time() - start_time_py),2)
                #print(str(nframe) + ' out of ' + str(total_frames) + ' frames processed | ' + str(fps) + ' FPS | Tracking Mode:  '+ str(get_tracking_mode(idle)) , end = "\r")
                print(str(nframe) + ' out of ' + str(total_frames) + ' frames processed | ' + str(fps) +' FPS | Tracking Mode:  '+ str(get_tracking_mode(idle)) +'        ' , end = '\r') 
 
     
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                
            else:
                print()
                print('Video has ended')
                break

        if not pt_cfg.POLYTRACK.CONTINUOUS_VIDEO:
            complete_tracking(predicted_position)
            predicted_position =[]
            pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS = []
            flowers_recorded = False

    cv2.destroyAllWindows()
    complete_tracking(predicted_position)
    end_time = datetime.now()
    print()
    print("End:  " + str(end_time))
    print("Processing Time:  " + str(end_time-start_time))
    processing_text.write("Start:  " + str(start_time) + "\n End time: " +  str(end_time)+ "\n Processing time: " + str(end_time-start_time)+ "\n Frames: " + str(video_frames))
    processing_text.close() 





if __name__ == '__main__':
    try:
        app.run(main)
    except:
        #removed SystemExit
        complete_tracking([])
        save_flowers()
        pass

