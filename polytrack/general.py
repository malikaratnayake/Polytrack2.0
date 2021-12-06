import numpy as np
import cv2
from polytrack.config import pt_cfg
import os
import datetime as dt
import math


def cal_dist(x,y,px,py):
    type(x)
    edx = float(x) - float(px)
    edy = float(y) - float(py)
    error = np.sqrt(edx**2+edy**2)
    
    return error


def predict_next(_for_predictions):
    
    _predicted = []
    for _insect in _for_predictions:
        _insect_num = _insect[0]
        _x0 = float(_insect[1])
        _y0 = float(_insect[2])
        _x1 = float(_insect[3])
        _y1 = float(_insect[4])
        
               
        Dk1 = np.transpose([_x0, _y0])
        Dk2 = np.transpose([_x1, _y1])
        A = [[2,0,-1,0],  [0,2,0,-1]]
        Dkc = np.concatenate((Dk1,Dk2))
        
#         print(Dk1,Dk2,Dkc)
        Pk = np.dot(A,Dkc.T)
        
        _predicted.append([_insect_num, Pk[0], Pk[1]])
        
    
    return _predicted


def check_idle(_nframe, _predicted_position):
    if ((_nframe >pt_cfg.POLYTRACK.INITIAL_FRAMES) and (bool(_predicted_position) == False) and not pt_cfg.POLYTRACK.IDLE_OUT):
        _idle = True

    else:
        _idle=False
        

        
    return _idle

def get_video_details(vid):
    pt_cfg.POLYTRACK.FRAME_WIDTH = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    pt_cfg.POLYTRACK.FRAME_HEIGHT = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #pt_cfg.POLYTRACK.FPS = int(vid.get(cv2.CAP_PROP_FPS))
    pt_cfg.POLYTRACK.FRAME_COUNT = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    print('Video dimensions: ', pt_cfg.POLYTRACK.FRAME_WIDTH, ' x ', pt_cfg.POLYTRACK.FRAME_HEIGHT)
    print('Frame rate: ', pt_cfg.POLYTRACK.FPS, 'fps')
    print('Video length: ', round(pt_cfg.POLYTRACK.FRAME_COUNT), 'frames')


    return pt_cfg.POLYTRACK.FRAME_WIDTH, pt_cfg.POLYTRACK.FRAME_HEIGHT, pt_cfg.POLYTRACK.FRAME_COUNT

def get_video_list(directory, video_extension):
    video_list = []
    for video in os.listdir(directory):
        if video.endswith(video_extension):
            video_list.append(video)

    video_list.sort()

    return video_list

def get_video_start_time(video_name, _starting_frame):
    record_time = dt.datetime.strptime(video_name.split('_')[5].split('.')[0], '%H%M%S').time()
    record_date = dt.datetime.strptime(video_name.split('_')[4].split('.')[0], '%Y%m%d').date()
    cam_number = video_name.split('_')[1]
    cam_direction = set_camera_direction(video_name.split('_')[2])
    # video_start_time = [record_time, _nframe]

    video_record_details = [cam_number, cam_direction, record_date,  record_time, _starting_frame]

    
    print("Record Time", record_time)
    print("Camera Number", cam_number)
    print("Camera Direction", cam_direction)
    print("Record Date", record_date)

    return video_record_details



def set_camera_direction(_direction_from_filename):
    if str(_direction_from_filename) == 'N':
        pt_cfg.POLYTRACK.FACING_NORTH = True
        _camera_direction = 'North'
    else:
        pt_cfg.POLYTRACK.FACING_NORTH = False
        _camera_direction = 'South'
    
    return _camera_direction


def cal_abs_time(_nframe, video_start):
    current_frame_in_video = _nframe - video_start[4]
    time_in_video = str(dt.timedelta(seconds=math.floor(current_frame_in_video/pt_cfg.POLYTRACK.FPS))) 

    video_start_time = dt.datetime.strptime(str(video_start[3]), '%H:%M:%S')
    time_in_video = dt.datetime.strptime(time_in_video, '%H:%M:%S')
    time_zero = dt.datetime.strptime('00:00:00', '%H:%M:%S')
    absolute_time = ((video_start_time - time_zero + time_in_video).time())

    return absolute_time

def assign_insect_num(_current_time, insect_count):

    day = int(pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS[2].day)
    cam = int(pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS[0])
    time_component = 1000*(_current_time.second + _current_time.minute*100 + _current_time.hour*10000 + day*1000000+ cam*100000000)
    insect_count_component = insect_count + 1

    insect_num = time_component + insect_count_component

    pt_cfg.POLYTRACK.INSECT_COUNT += 1

    return insect_num

def assign_datapoint_name():

    day = int(pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS[2].day)
    cam = int(pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS[0])

    dp_name = cam*100+day

    return dp_name

def check_sight_coordinates(_record, outside_spot = True):

    if pt_cfg.POLYTRACK.DL_DARK_SPOTS:
            
        _x = int(float(_record[0]))
        _y = int(float(_record[1]))

        dark_spots = pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS
        spot_radius = int(pt_cfg.POLYTRACK.DL_DARK_SPOTS_RADIUS)

        for spot in dark_spots:
            spot_x = spot[0]
            spot_y = spot[1]

            if (cal_dist(_x,_y,spot_x,spot_y) <= spot_radius):
                outside_spot = False
                break
            else:
                pass
    
    else:
        outside_spot = True

    return outside_spot


def reverse_video(nframe, vid, idle, new_insect, video_start_frame):

    if idle and (len(new_insect)>0):
        nframe = nframe - 30
        reset_frame = nframe - video_start_frame
        vid.set(1, reset_frame)
        #vid.set(1, nframe)
        idle = False
        new_insect = []
        pt_cfg.POLYTRACK.IDLE_OUT = True
        #reset_bg_model()
        #print('ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')

    else:
        pass

    return nframe, idle, new_insect



def get_tracking_mode(_idle):
    if _idle:
        tracking_mode = "Low-resolution     "
    else:
        tracking_mode = "High-resolution    "

    return tracking_mode
