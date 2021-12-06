import numpy as np
# import cv2
from polytrack.general import cal_dist
from polytrack.flowers import flowers
import os
import datetime as dt
from polytrack.flowers import get_flower_details
from polytrack.config import pt_cfg
from operator import itemgetter
import pandas as pd
from polytrack.general import cal_abs_time


if pt_cfg.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER: flower_entry_exit = pd.DataFrame(columns = ['nframe', 'flower','insect_num','entry_time','exit_time'])


def check_on_flower(_coordinates):
    _x = _coordinates[0]
    _y = _coordinates[1]
    foraging_flowers = []

    _flowers = get_flower_details()


    for flower in _flowers:
        dist_from_c = cal_dist(_x,_y,flower[1],flower[2])
        if dist_from_c <=  flower[3]*pt_cfg.POLYTRACK.FLOWER_RADIUS_THRESHOLD:
            foraging_flowers.insert(len(foraging_flowers),[flower[0],dist_from_c])
        else:
            pass


    current_flower = evaluate_flowers(foraging_flowers)

   
    return current_flower


def evaluate_flowers(_foraging_flowers):
    if (_foraging_flowers):
        if (len(_foraging_flowers) == 1):
            _current_flower = _foraging_flowers[0][0]
        else:
            _current_flower = sorted(_foraging_flowers, key=itemgetter(1))[0][0]
    else:
        _current_flower = np.nan

    return _current_flower






def update_visit_num(_flower_current, _insect_num,_insect_tracks):
    if np.isnan(_flower_current):
        _visit_number = np.nan
    else:
        previously_visited = _insect_tracks[_insect_tracks['insect_num'] == _insect_num].flower.dropna()
        if bool(len(previously_visited.values)):
            _last_visited_flower = previously_visited.iloc[-1]
            if (_last_visited_flower != _flower_current):
                previously_visited_unique = previously_visited.unique()
                if (_flower_current in previously_visited_unique):
                    _visit_number = _insect_tracks['visit_num'][_insect_tracks.loc[(_insect_tracks['insect_num'] == _insect_num) & (_insect_tracks['flower'] == _flower_current), 'flower'].last_valid_index()]+1
                else:
                    _visit_number = 1
            else:
                _visit_number = _insect_tracks['visit_num'][_insect_tracks.loc[(_insect_tracks['insect_num'] == _insect_num) & (_insect_tracks['flower'] == _flower_current), 'flower'].last_valid_index()]
        else:
            _visit_number = 1

    return _visit_number


def record_entry_exit(_nframe, _current_flower,_insect_tracks, _insect_num, new_insect=False):
    current_position = _current_flower
    last_frame_position = _insect_tracks[_insect_tracks['insect_num'] == _insect_num].flower.values[-1]

    if not np.isnan(current_position) and np.isnan(last_frame_position):
        print(_nframe, "Entered the flower", _insect_num, last_frame_position, current_position, cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS))
        entry_record = [_nframe, current_position, _insect_num,  cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS), np.nan]
        flower_entry_exit.loc[len(flower_entry_exit)] = entry_record

    elif not np.isnan(current_position) and new_insect:
        print(_nframe, "Entered the flower throgh new insect", _insect_num, last_frame_position, current_position, cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS))
        entry_record = [_nframe, current_position, _insect_num,  cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS), np.nan]
        flower_entry_exit.loc[len(flower_entry_exit)] = entry_record

    elif np.isnan(current_position) and not np.isnan(last_frame_position):
        flower_entry_record = flower_entry_exit.loc[(flower_entry_exit['flower'] == int(last_frame_position)) & (flower_entry_exit['insect_num'] == _insect_num)].last_valid_index()
        print(last_frame_position, _insect_num, flower_entry_record)
        flower_entry_exit.loc[flower_entry_record,'exit_time'] = cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS)
        # print(_nframe, "exited the flower", _insect_num, last_frame_position, current_position, cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS))
    else:
        pass



def save_flower_entry_exit():

    flower_entry_exit.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'flower_entry_exit.csv', sep=',')

    return None
