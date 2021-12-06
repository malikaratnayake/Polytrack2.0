import cv2
import random
import colorsys
import numpy as np
import pandas as pd
from polytrack.config import pt_cfg
from polytrack.deep_learning import detect_deep_learning
from polytrack.record import track_frame
from polytrack.track import associate_detections_DL, Hungarian_method
from polytrack.general import cal_dist, assign_datapoint_name
flowers = pd.DataFrame(columns = ['flower_num', 'x0','y0','radius','species','confidence'])
flower_tracks = pd.DataFrame(columns = ['nframe','flower_num', 'x0','y0','radius','species','confidence'])


def record_flowers(vid, video_name):

    vid.set(1, 6000)
    ret, frame = vid.read()
    flower_positions = sorted(detect_deep_learning(frame, True), key=lambda x: float(x[0]))
    

    for position in flower_positions:
        flower_num = len(flowers)
        _x = int(float(position[0]))
        _y = int(float(position[1]))
        _radius = int(float(position[2])*pt_cfg.POLYTRACK.FLOWER_THRESH_FACTOR)
        _species = position[3]
        _confidence = float(position[4])

        flower_record = [flower_num, _x, _y, _radius, _species, _confidence]
        flower_tracks_record = [1,flower_num, _x, _y, _radius, _species, _confidence]
        # flowers.loc[len(flowers)] = flower_record
        # flower_tracks.loc[len(flower_tracks)] = flower_tracks_record

        cv2.circle(track_frame, (_x,_y), int(_radius), (0,0,255), 4)
        cv2.putText(track_frame, 'F' + str(flower_num), (_x+_radius, _y), cv2.FONT_HERSHEY_DUPLEX , 0.7, (0,255,255), 1, cv2.LINE_AA)

    
    
    flowers.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+str(video_name)+'_flowers.csv', sep=',') #Save the csv file with insect track

    cv2.imwrite(str(pt_cfg.POLYTRACK.OUTPUT)+str(video_name)+'_flowers.png', cv2.add(frame,track_frame))

    print(str(len(flowers))+' flowers Recorded')

    return flowers, bool(len(get_flower_details()))

def get_flower_details():
    
    _recorded_flowers = flower_tracks[['flower_num', 'x0','y0','radius']].loc[flower_tracks['nframe'] == flower_tracks.nframe.max()].values.tolist()

    return _recorded_flowers


def track_flowers(_nframe, frame):

    flower_positions_dl = sorted(detect_deep_learning(frame, True), key=lambda x: float(x[0]))

    associations_DL, missing, not_associated  = associate_detections_DL(flower_positions_dl, get_flower_details(), pt_cfg.POLYTRACK.FLOWER_MOVEMENT_THRESHOLD)

    record_flower_positions(_nframe, associations_DL, missing, not_associated)



def update_flower_master():
    num_of_flowers = flower_tracks['flower_num'].max()

    if not np.isnan(num_of_flowers):

        for flower in np.arange(0,num_of_flowers+1,1):
            last_pos_index = flower_tracks.loc[flower_tracks['flower_num'] == flower].last_valid_index()
            last_pos_record = flower_tracks.iloc[last_pos_index].values.tolist()

            flowers.loc[flower, 'flower_num': 'confidence'] =  last_pos_record[1:]
            

            cv2.circle(track_frame, (last_pos_record[2],last_pos_record[3]), int(last_pos_record[4]), (0,0,255), 4)
            cv2.putText(track_frame, 'F' + str(last_pos_record[1]), (last_pos_record[2]+last_pos_record[4], last_pos_record[3]), cv2.FONT_HERSHEY_DUPLEX , 0.7, (0,255,255), 1, cv2.LINE_AA)

    else:
        pass



def record_flower_positions(_nframe, _associations_DL, _missing, _not_associated):
    
    for ass_d in _associations_DL:
        _flower_num = int(float(ass_d[0]))
        _x = int(float(ass_d[1]))
        _y = int(float(ass_d[2]))
        _radius = int(float(ass_d[3]))
        _species = ass_d[4]
        _confidence = ass_d[5]

        flower_record = [_nframe, _flower_num, _x, _y, _radius, _species, _confidence]
        flower_tracks.loc[len(flower_tracks)] = flower_record

 
    for miss in _missing:
        _flower_num = miss
        last_pos_details = flower_tracks.loc[flower_tracks['flower_num'] == _flower_num].iloc[-1].values.tolist()

        _x = int(float(last_pos_details[2]))
        _y = int(float(last_pos_details[3]))
        _radius = int(float(last_pos_details[4]))
        _species = last_pos_details[5]
        _confidence = last_pos_details[6]
        
        flower_record = [_nframe, _flower_num, _x, _y, _radius, _species, _confidence]
        flower_tracks.loc[len(flower_tracks)] = flower_record


            
    _not_associated = sorted(_not_associated, key=lambda x: float(x[0]))

    for nass in _not_associated:
        _flower_num = flower_tracks['flower_num'].max()+1
        if np.isnan(_flower_num): _flower_num=0

        _x = int(float(nass[0]))
        _y = int(float(nass[1]))
        _radius = int(float(nass[2]))
        _species = nass[3]
        _confidence = nass[4]
        
        flower_record = [_nframe, _flower_num, _x, _y, _radius, _species, _confidence]
        flower_tracks.loc[len(flower_tracks)] = flower_record

    update_flower_master()








# def associate_flowers(_detections, _predictions):
#     _missing = [] 
#     _assignments = Hungarian_method(_detections, _predictions)
#     _insects = [i[0] for i in _predictions]
    
#     _not_associated = np.zeros(shape=(0,5))
#     for _nass in (_assignments[len(_insects):]):
#         _not_associated = np.vstack([_not_associated,(_detections[_nass])])
                               
    
#     _associations_DL = np.zeros(shape=(0,6))
#     for ass in np.arange(len(_insects)):
#         _record = _assignments[ass]

#         if (_record <= len(_detections)-1):
#             _xc, _yc, _area, _lable, _conf = _detections[_assignments[ass]][0],_detections[_assignments[ass]][1],_detections[_assignments[ass]][2],_detections[_assignments[ass]][3],_detections[_assignments[ass]][4]
#             # _dist = cal_dist(_xc,_yc,_predictions[ass][1],_predictions[ass][2])
#             # if(_dist>50):
#             #     _missing.append(_predictions[ass][0])
#             # else:
#             _associations_DL = np.vstack([_associations_DL,(_predictions[ass][0],_detections[_assignments[ass]][0],_detections[_assignments[ass]][1],_detections[_assignments[ass]][2],_detections[_assignments[ass]][3],_detections[_assignments[ass]][4])])
                
#         else:
#             _missing.append(_predictions[ass][0])

#     return _associations_DL, _missing, _not_associated







def get_flowers():
    flower_details = flowers[['flower_num', 'x0','y0','radius']].values

    return flower_details

def update_flower_analysis(_insect_track, _insectname):
    flowers[str(_insectname)+'_time'] = np.nan
    flowers[str(_insectname)+'_visits'] = np.nan

    for flower in np.arange(0, len(flowers),1):
        flowers.iloc[flower, flowers.columns.get_loc(str(_insectname)+'_time')] = len(_insect_track[_insect_track['flower'] == flower])
        flowers.iloc[flower, flowers.columns.get_loc(str(_insectname)+'_visits')] =  _insect_track['visit_num'][_insect_track['flower'] == flower].max()


    return None

def save_flowers():
    flowers.insert(flowers.columns.get_loc('y0')+1,'y_adj', ((1080-flowers['y0'])) if pt_cfg.POLYTRACK.FACING_NORTH else flowers['y0'])
    flowers.insert(flowers.columns.get_loc('confidence')+1,'Total_time',flowers[[col for col in flowers.columns if col.endswith('_time')]].sum(axis=1))
    flowers.insert(flowers.columns.get_loc('Total_time')+1,'Total_visits', flowers[[col for col in flowers.columns if col.endswith('_visits')]].sum(axis=1))
    flowers.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'flowers_'+str(assign_datapoint_name())+'.csv', sep=',')
    flower_tracks.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'flowes_tracks_'+str(assign_datapoint_name())+'.csv', sep=',')



    return None


