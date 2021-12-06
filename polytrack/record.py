import cv2
import random
import colorsys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Circle
from polytrack.config import pt_cfg
from polytrack.general import cal_abs_time, assign_insect_num,cal_dist, assign_datapoint_name, check_sight_coordinates
# from polytrack.general import cal_dist
track_frame = np.zeros((1080,1920,3), np.uint8)
from polytrack.flowers import get_flower_details, update_flower_analysis, save_flowers, flowers
from polytrack.analysis import check_on_flower, update_visit_num, record_entry_exit, save_flower_entry_exit
from datetime import datetime
#output_dir = pt_cfg.POLYTRACK.OUTPUT
edge_pixels = pt_cfg.POLYTRACK.EDGE_PIXELS
width, height, fps = pt_cfg.POLYTRACK.FRAME_WIDTH, pt_cfg.POLYTRACK.FRAME_HEIGHT, pt_cfg.POLYTRACK.FPS
max_occlusions = pt_cfg.POLYTRACK.MAX_OCCLUSIONS
max_occlusions_edge = pt_cfg.POLYTRACK.MAX_OCCLUSIONS_EDGE
output_video = pt_cfg.POLYTRACK.SHOW_TRACK_FRAME or pt_cfg.POLYTRACK.SHOW_VIDEO_OUTPUT or pt_cfg.POLYTRACK.SAVE_TRACK_FRAME or pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT
insect_tracks = pd.DataFrame(columns = ['nframe', 'insect_num','x0','y0','area','species','confidence','status','model','flower','visit_num'])
if pt_cfg.POLYTRACK.SIGHTING_TIMES: insects_sightings = pd.DataFrame(columns = ['species', 'insect_num','start_time','end_time'])
if pt_cfg.POLYTRACK.INSECT_VERIFICATION: dropped_insects = []
# if pt_cfg.POLYTRACK.DL_DARK_SPOTS: dark_spots = []



def setup_video_save(output_directory):

    if pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT:

        now = datetime.now()
        current_time = now.strftime("%H%M%S")
        codec = cv2.VideoWriter_fourcc(*pt_cfg.POLYTRACK.VIDEO_WRITER)
        global out_video
        out_video = cv2.VideoWriter(str(output_directory)+'video_'+str(assign_datapoint_name())+'.avi', codec, fps, (width, height))
        pt_cfg.POLYTRACK.VIDEO_OUTPUT_SETUP = True
        #print(str(pt_cfg.POLYTRACK.OUTPUT))

    if pt_cfg.POLYTRACK.SAVE_TRACK_FRAME:
        codec = cv2.VideoWriter_fourcc(*pt_cfg.POLYTRACK.VIDEO_WRITER)
        out_track = cv2.VideoWriter(str(pt_cfg.POLYTRACK.OUTPUT)+'track.avi', codec, fps, (width, height))

def record_track(frame,_nframe, _associated_det_BS, _associated_det_DL, _missing, _new_insect,idle):
    
    #Record Data

    if output_video: 
        details_frame = np.zeros((1080,1920,3), np.uint8)
    else:
        details_frame = None
    
    record_BS_detections(_nframe, details_frame, _associated_det_BS)
    record_DL_detections(_nframe, details_frame, _associated_det_DL)
    record_missing(_nframe, _missing)
    record_new_insect(frame,_nframe, _new_insect)

    
    if output_video: process_output_video(frame, track_frame, details_frame, _nframe, idle)
    
    #insect_tracks.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'tracks.csv', sep=',')

    _for_predictions = get_data_predictions(_nframe)

    if pt_cfg.POLYTRACK.INSECT_VERIFICATION and (_nframe % pt_cfg.POLYTRACK.INSECT_VERIFICATION_INTERVAL == 0):
        _for_predictions = verify_insects(_for_predictions)
    
    return _for_predictions


def verify_insects(for_predictions):

    _verified_predictions = np.empty([0,5])
    dark_spots = pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS

    for prediction in for_predictions:
        insect_num = prediction[0]
        total_records = len(insect_tracks[(insect_tracks.insect_num == insect_num)])
        bs_ratio = len(insect_tracks[(insect_tracks.insect_num == insect_num) & (insect_tracks.model == 'BS')])/total_records
        not_on_flower = np.isnan(check_on_flower([prediction[1], prediction[2]]))
        #print(total_records, bs_ratio, not_on_flower)


        if (total_records >= pt_cfg.POLYTRACK.INSECT_VERIFICATION_MIN_FRAMES) and (bs_ratio < pt_cfg.POLYTRACK.INSECT_VERIFICATION_MIN_BS) and not_on_flower:
            last_detections = get_last_detections(insect_num, pt_cfg.POLYTRACK.INSECT_VERIFICATION_LAST_FRAMES)
            if cal_cum_distance(last_detections) <= pt_cfg.POLYTRACK.INSECT_VERIFICATION_THRESHOLD_CUM_DISTANCE:
                dropped_insects.append(insect_num)

                if pt_cfg.POLYTRACK.DL_DARK_SPOTS: dark_spots.append(get_dark_spot(prediction))
            else:
                _verified_predictions = np.vstack([_verified_predictions,(prediction)])
        else:
            _verified_predictions = np.vstack([_verified_predictions,(prediction)])

    pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS = dark_spots
    #print('dark_spots', dark_spots)

    
    return _verified_predictions





def get_last_detections(_insect_num, _num_frames):
    _last_detections = insect_tracks[(insect_tracks['insect_num'] == _insect_num) & (insect_tracks['status'] == 'In' )][insect_tracks.columns[2:4]][-min(len(insect_tracks[(insect_tracks['insect_num'] == _insect_num)]),_num_frames):].values

    return _last_detections


def cal_cum_distance(_last_detections):
    cum_distance = 0
    for _d in np.arange(0,len(_last_detections)-1,1):
        cum_distance += cal_dist(_last_detections[_d][0],_last_detections[_d][1],_last_detections[_d+1][0],_last_detections[_d+1][1])

    return cum_distance




def get_dark_spot(_prediction):
    x0 = insect_tracks['x0'][insect_tracks[(insect_tracks.insect_num == _prediction[0])].first_valid_index()]
    y0 = insect_tracks['y0'][insect_tracks[(insect_tracks.insect_num == _prediction[0])].first_valid_index()]

    if output_video: cv2.circle(track_frame, (int(x0), int(y0)), int(pt_cfg.POLYTRACK.DL_DARK_SPOTS_RADIUS), (255,255,255), 0)

    return [x0,y0]



def process_output_video(frame, track_frame,details_frame, _nframe, idle):

    track_frame, display_frame = prepare_output_video(frame, track_frame, details_frame, _nframe)

    if pt_cfg.POLYTRACK.SHOW_TRACK_FRAME:
        cv2.imshow("PolyTrack - Insect Tracks only", cv2.resize(track_frame, (pt_cfg.POLYTRACK.VIDEO_OUTPUT_WIDTH, pt_cfg.POLYTRACK.VIDEO_OUTPUT_HEIGHT)))
    
    if pt_cfg.POLYTRACK.SHOW_VIDEO_OUTPUT:
        cv2.imshow("PolyTrack - Insect Tracks", cv2.resize(display_frame, (pt_cfg.POLYTRACK.VIDEO_OUTPUT_WIDTH, pt_cfg.POLYTRACK.VIDEO_OUTPUT_HEIGHT)))

    if pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT and not idle and not pt_cfg.POLYTRACK.IDLE_OUT:
        #pt_cfg.POLYTRACK.SAVE_VIDEO_OUTPUT and not idle and not pt_cfg.POLYTRACK.IDLE_OUT
        out_video.write(display_frame)
        
    if pt_cfg.POLYTRACK.SAVE_TRACK_FRAME and not idle:
        out_track.write(track_frame)



def prepare_output_video(frame, track_frame, details_frame, _nframe):
    
    details_frame = cv2.putText(details_frame, 'Frame: ' +str(_nframe) + '| Time' +str(cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS)), (20, 20), cv2.FONT_HERSHEY_DUPLEX , 0.8, (255,255,255), 1, cv2.LINE_AA)
    track_frame = cv2.add(details_frame,track_frame)
    display_frame = cv2.add(frame, track_frame)

    return track_frame, display_frame


def complete_tracking(_predicted_position):

    print('======== Tracking Completed ======== ')
    _tracking_insects = [int(i[0]) for i in _predicted_position]
    
    
    for _insect in _tracking_insects:
        save_track(_insect)

    save_flowers()
    if pt_cfg.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER: save_flower_entry_exit()

    if pt_cfg.POLYTRACK.SIGHTING_TIMES: insects_sightings.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'sight_times.csv', sep=',')

    insect_tracks.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+'tracks.csv', sep=',')


def get_data_predictions(_nframe):
    
    _for_predictions = np.empty([0,5])
    _active_insects = list(set(insect_tracks.loc[(insect_tracks['nframe'] == _nframe)&(insect_tracks['status'] == 'In')]['insect_num'].values.tolist()))
    _missing_insects = list(set(insect_tracks.loc[(insect_tracks['nframe'] == _nframe)&(insect_tracks['status'] == 'missing')]['insect_num'].values.tolist()))
    #print(_nframe, _active_insects, _missing_insects)
    
    for insect in _active_insects:
        _x0 = insect_tracks.loc[insect_tracks['insect_num'] == insect].iloc[-1]['x0']
        _y0 = insect_tracks.loc[insect_tracks['insect_num'] == insect].iloc[-1]['y0']

        if not np.isnan(_x0):

            _past_detections = len(insect_tracks.loc[insect_tracks['insect_num'] == insect])
            
            if(_past_detections>=2):
                _x1 = float(insect_tracks.loc[insect_tracks['insect_num'] == insect].iloc[-2]['x0'])
                _y1 = float(insect_tracks.loc[insect_tracks['insect_num'] == insect].iloc[-2]['y0'])

                
                if np.isnan(_x1):
                    _x1  =_x0 
                    _y1 =_y0
                    
                else:
                    _x1 = int(_x1)
                    _y1 = int(_y1)
                    

            else:
                _x1=_x0 
                _y1=_y0

                
            _for_predictions = np.vstack([_for_predictions,(insect,_x0,_y0,_x1,_y1)])
            if output_video: cv2.line(track_frame,(int(_x1),int(_y1)),(int(_x0),int(_y0)),track_colour(insect),2)
        
        else:
            pass



    
    if (_missing_insects):
        for insect in _missing_insects:
            _x0m = _x1m = insect_tracks['x0'][insect_tracks.loc[insect_tracks['insect_num'] == insect, 'x0'].last_valid_index()]
            _y0m = _y1m = insect_tracks['y0'][insect_tracks.loc[insect_tracks['insect_num'] == insect, 'y0'].last_valid_index()]

            _for_predictions = np.vstack([_for_predictions,(insect,_x0m,_y0m,_x1m,_y1m)])
    
    return _for_predictions


def track_colour(_insect_num):
    
    if (_insect_num <= 5):
        _colour_code = (_insect_num*5)%6
    else:
        _colour_code = _insect_num%6
    
 
    if(_colour_code ==0): _colour = (255,0,0)
    elif(_colour_code ==1): _colour = (0,255,0)
    elif(_colour_code ==2): _colour = (0,0,255)
    elif(_colour_code ==3): _colour = (0,255,255)
    elif(_colour_code ==4): _colour = (255,0,255)
    else: _colour = (255,255,0)
    
    return _colour

def record_BS_detections(_nframe, details_frame, _associated_det_BS):
    
    for record in _associated_det_BS:
        _insect_num = int(float(record[0]))
        _x = int(float(record[1]))
        _y = int(float(record[2]))
        _area = int(float(record[3]))
        _species = insect_tracks['species'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'species'].last_valid_index()]
        _confidence = np.nan
        _status = 'In'
        _model = 'BS'
        _flower, _visit_number = update_analysis(_nframe, _insect_num, [_x,_y], insect_tracks)
        
        
        if output_video:
            cv2.circle(track_frame, (_x, _y), 3, track_colour(_insect_num), 2)
            cv2.putText(details_frame, str(_species)+' ' + str(_insect_num)+' BS', (_x+20, _y+20), cv2.FONT_HERSHEY_DUPLEX , 0.7, track_colour(_insect_num), 1, cv2.LINE_AA) 

        
        insect_record_BS = [_nframe, _insect_num, _x, _y, _area, _species, _confidence, _status, _model,_flower, _visit_number]
        insect_tracks.loc[len(insect_tracks)] = insect_record_BS
        


def update_analysis(_nframe, _insect_num, _coordinates,_insect_tracks):

    if pt_cfg.POLYTRACK.ANALYSE_POLLINATION:

        if (_nframe % pt_cfg.POLYTRACK.ANALYSIS_UPDATE_FREQUENCY == 0):
            _flower_current = check_on_flower(_coordinates)
            _visit_number = update_visit_num(_flower_current, _insect_num,_insect_tracks)
            if pt_cfg.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER: record_entry_exit(_nframe, _flower_current,_insect_tracks, _insect_num)
        

        else:
            _flower_current = _insect_tracks.loc[_insect_tracks['insect_num'] == _insect_num].iloc[-1]['flower']
            _visit_number = _insect_tracks.loc[_insect_tracks['insect_num'] == _insect_num].iloc[-1]['visit_num']

    else:
        _flower_current, _visit_number = np.nan, np.nan

    return _flower_current, _visit_number






def record_DL_detections(_nframe, details_frame, _associated_det_DL):
    
    for record in _associated_det_DL:
        _insect_num = int(float(record[0]))
        _x = int(float(record[1]))
        _y = int(float(record[2]))
        _area = int(float(record[3]))
        _species = record[4]
        _confidence = float(record[5])
        _status = 'In'
        _model = 'DL'
        _flower,_visit_number = update_analysis(_nframe, _insect_num, [_x,_y], insect_tracks) 
        
        
        if output_video:
            cv2.circle(track_frame, (_x, _y), 3, track_colour(_insect_num), 2)
            cv2.putText(details_frame, str(_species)+' ' + str(_insect_num)+' DL', (_x+20, _y+20), cv2.FONT_HERSHEY_DUPLEX , 0.7, track_colour(_insect_num), 1, cv2.LINE_AA) 

        insect_record_DL = [_nframe, _insect_num, _x, _y, _area, _species, _confidence, _status, _model, _flower, _visit_number]
        insect_tracks.loc[len(insect_tracks)] = insect_record_DL
        

def record_missing(_nframe, _missing):
    
    for record in _missing:
        _insect_num = int(float(record))
        _x = np.nan
        _y = np.nan
        _area = np.nan
        _species = insect_tracks['species'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'species'].last_valid_index()]
        _confidence = np.nan
        _status = evaluate_missing(_nframe, _insect_num)
        _model = np.nan
        _flower, _visit_number = np.nan, np.nan
        
        insect_record_missing = [_nframe, _insect_num, _x, _y, _area, _species, _confidence, _status, _model,_flower, _visit_number]
        insect_tracks.loc[len(insect_tracks)] = insect_record_missing 



    
def record_new_insect(_frame,_nframe, _new_insect):

    if len(_new_insect)>0 : pt_cfg.POLYTRACK.IDLE_OUT = False
    
    for record in _new_insect:
        
        if check_sight_coordinates(record): #verify whether detection is not false positive
            
            # _insect_num = insect_tracks['insect_num'].max()+1
            current_time = cal_abs_time(_nframe, pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS)
            _insect_num = assign_insect_num(current_time, pt_cfg.POLYTRACK.INSECT_COUNT)
            
            # if np.isnan(_insect_num): _insect_num=0
                
            _x = int(float(record[0]))
            _y = int(float(record[1]))
            _area = int(float(record[2]))
            _species = record[3]
            _confidence = float(record[4])
            _status = 'In'
            _model = 'DL'
            _flower = check_on_flower([_x,_y])
            _visit_number = np.nan if np.isnan(_flower) else 1
            
            # _, _ = update_analysis(_nframe, _insect_num, [_x,_y], insect_tracks)
            #print(_nframe,_insect_num, _x, _y,_species,_confidence)
            manual_verification(_frame,_insect_num, _x, _y,_species,_confidence)
            
            if output_video:
                cv2.circle(track_frame, (int(float(_x)), int(float(_y))), 4, track_colour(_insect_num), 4)
                cv2.putText(track_frame, str(_species)+' ' + str(_insect_num), (_x+20, _y+20), cv2.FONT_HERSHEY_DUPLEX , 0.7, track_colour(_insect_num), 1, cv2.LINE_AA) 

            insect_record_new = [_nframe, _insect_num, _x, _y, _area, _species, _confidence, _status, _model,_flower, _visit_number]
            insect_tracks.loc[len(insect_tracks)] = insect_record_new

            if pt_cfg.POLYTRACK.SIGHTING_TIMES:
                new_insect = [_species, _insect_num, current_time, np.nan]
                insects_sightings.loc[len(insects_sightings)] = new_insect  

            if pt_cfg.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER: record_entry_exit(_nframe, _flower,insect_tracks, _insect_num, new_insect=True)

        else:
            pass   
        



        

        
def manual_verification(_frame,_insect_num, _x, _y,_species,_confidence):
    _insect_image = _frame[max(_y-50,1):min(_y+50,1079), max(_x-50,1):min(_x+50,1919)]
    _filename= str(_species)+'_'+str(_insect_num)+'_img.png'
    cv2.imwrite(str(pt_cfg.POLYTRACK.OUTPUT)+str(_filename), _insect_image)
    

def evaluate_missing(_nframe, _insect_num):
    
    #check whether it has left the frame (last appearence in the edge and being missing for more than 15 frames)
    _last_edge_det = last_det_check(_insect_num)
    _missing_frames = _nframe - insect_tracks['nframe'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'x0'].last_valid_index()]
    
    if ((_last_edge_det==True)&(_missing_frames>max_occlusions_edge)) and not pt_cfg.POLYTRACK.NOISY:
        _status ='out'
        save_track(_insect_num)
        
    elif(_missing_frames>max_occlusions) and not pt_cfg.POLYTRACK.NOISY:
        _status ='out'
        save_track(_insect_num)
    
    else:
        _status = 'missing'
        
    return _status
    

def save_track(_insect_num):

    _insect_track = insect_tracks.loc[insect_tracks['insect_num'] == _insect_num].reset_index()
    #_insect_track = _insect_track[:_insect_track['x0'].last_valid_index()+1]
    _species = insect_tracks['species'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'confidence'].idxmax()]
    _insect_track.insert(6,'y_adj', (height-_insect_track['y0']) if pt_cfg.POLYTRACK.FACING_NORTH else _insect_track['y0'])
    _insectname = str(_species)+'_'+str(_insect_num)

    if pt_cfg.POLYTRACK.FILTER_TRACKS:
        last_detections = get_last_detections(_insect_num, pt_cfg.POLYTRACK.FILTER_TRACKS_VERIFY_FRAMES)

        if cal_cum_distance(last_detections) >= pt_cfg.POLYTRACK.FILTER_TRACKS_DIST_THRESHOLD:
            # _insectname = str(_species)+'_'+str(_insect_num)
            _insect_track.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+str(_insectname)+'.csv', sep=',') #Save the csv file with insect track

        else:
            pass
    
    else:
        # _insectname = str(_species)+'_'+str(_insect_num)
        _insect_track.to_csv(str(pt_cfg.POLYTRACK.OUTPUT)+str(_insectname)+'.csv', sep=',') #Save the csv file with insect track

    
    
    if pt_cfg.POLYTRACK.SIGHTING_TIMES:
        exit_time = cal_abs_time(_insect_track['nframe'][_insect_track.loc[_insect_track['insect_num'] == _insect_num, 'x0'].last_valid_index()], pt_cfg.POLYTRACK.CURRENT_VIDEO_DETAILS)
        insects_sightings.loc[insects_sightings['insect_num'] == _insect_num, 'end_time'] = exit_time

   
    if pt_cfg.POLYTRACK.PLOT_GRAPH: plot_path(_insect_track, _insectname)

    if pt_cfg.POLYTRACK.UPDATE_FLOWER_ANALYSIS: update_flower_analysis(_insect_track, _insectname)
    
    del _insect_track

    
# def finish_tracking(_predicted_position):
#     _tracking_insects = [int(i[0]) for i in _predicted_position]
    
#     for _insect in _tracking_insects:
#         save_track(_insect)
            
    
def plot_path(_insect_track, _insectname):
    plt.figure(figsize=(20,10))
    plt.scatter(_insect_track['x0'], _insect_track['y_adj'], c=_insect_track['nframe'],  cmap='RdYlBu_r', label = 'Recorded Path')
    plt.plot(_insect_track['x0'], _insect_track['y_adj'])

    currentAxis = plt.gca()
    # y_coord = pt_cfg.POLYTRACK.FRAME_HEIGHT-flowers['y0'][0] if pt_cfg.POLYTRACK.FACING_NORTH else flowers['y0'][0]
    # currentAxis.add_patch(Circle((flowers['x0'][0] , y_coord), radius = (flowers['radius'][0]), fill=True, alpha = 0.2, label = 'Flowers'))
    # currentAxis.add_patch(Circle((flowers['x'][0]/ppmm , (1080-flowers['y'][0])/ppmm), radius = (flw_thres+30)/ppmm, fill=False, alpha = 0.8))
    for row in np.arange(0,len(flowers),1):
        y_coord = pt_cfg.POLYTRACK.FRAME_HEIGHT-flowers['y0'][row] if pt_cfg.POLYTRACK.FACING_NORTH else flowers['y0'][row]
        currentAxis.add_patch(Circle((flowers['x0'][row] , y_coord), radius = (flowers['radius'][row]), fill=True, alpha = 0.2, label = '_nolegend_'))
        # currentAxis.add_patch(Circle((flowers['x'][row]/ppmm , (1080-flowers['y'][row])/ppmm), radius = (flw_thres+30)/ppmm, fill=True, alpha = 0.2, label = '_nolegend_'))
        # currentAxis.add_patch(Circle((flowers['x'][row]/ppmm , (1080-flowers['y'][row])/ppmm), radius = (flw_thres+30)/ppmm, fill=False, alpha = 0.8))

        currentAxis.annotate(flowers['flower_num'][row], (flowers['x0'][row] , (flowers['radius'][row]+ y_coord)),xytext=(flowers['radius'][row]/2, flowers['radius'][row]/2), fontsize =20,textcoords='offset points',
        bbox=dict(boxstyle="round", fc="0.8"),
        arrowprops=dict(arrowstyle="->",
                        connectionstyle="angle,angleA=0,angleB=90,rad=10"))



    plt.legend()
    plt.grid()
    plt.colorbar()
    plt.xlim(0,1920)
    plt.ylim(0,1080)
    plt.title('Movement Path '+str(_insectname), fontsize=25)
    plt.xlabel('X position (pixels)', fontsize=16)
    plt.ylabel('Y position (pixels)', fontsize=16)
    plt.tight_layout()    
    plt.savefig(str(pt_cfg.POLYTRACK.OUTPUT)+str(_insectname)+'.png', format='png', dpi=100)
    #plt.show()



def last_det_check(_insect_num):
    
    in_edge = False
    
    last_x = insect_tracks['x0'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'x0'].last_valid_index()]
    last_y = insect_tracks['y0'][insect_tracks.loc[insect_tracks['insect_num'] == _insect_num, 'y0'].last_valid_index()]
    
    if ((last_x < edge_pixels) or (last_x > (width-edge_pixels))):
        in_edge = True
    elif ((last_y < edge_pixels) or (last_y > (height-edge_pixels))):
        in_edge = True
    else:
        in_edge = False
        
    return in_edge


