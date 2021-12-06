#! /usr/bin/env python
# coding=utf-8
from easydict import EasyDict as edict


__PT                           = edict()
# Consumers can get config by: from config import cfg

pt_cfg                           = __PT

# POLYTRACK options
__PT.POLYTRACK                 = edict()

__PT.POLYTRACK.INPUT          = './data/video/video_24_2.mp4'
#__PT.POLYTRACK.INPUT_DIR      = './data/video/'
__PT.POLYTRACK.INPUT_DIR      = '/home/mrat0006/bm75_scratch/Sunny_Ridge_March2021/17March2021/Cam_4/converted/'
#__PT.POLYTRACK.INPUT_DIR      = '/home/mrat0006/bm75/Polytrack/data/video/'
__PT.POLYTRACK.VIDEO_EXT      = 'avi'
__PT.POLYTRACK.CONTINUOUS_VIDEO = True
__PT.POLYTRACK.OUTPUT         = '/home/mrat0006/bm75_scratch/Sunny_Ridge_March2021/17March2021/Cam_4/reruns/'
__PT.POLYTRACK.VIDEO_START_TIME = None
__PT.POLYTRACK.CURRENT_VIDEO_DETAILS = None
__PT.POLYTRACK.INSECT_COUNT = 0

#Displaying output video
__PT.POLYTRACK.SHOW_TRACK_FRAME      = False
__PT.POLYTRACK.SHOW_VIDEO_OUTPUT     = True
__PT.POLYTRACK.VIDEO_OUTPUT_WIDTH    = 1280
__PT.POLYTRACK.VIDEO_OUTPUT_HEIGHT   = 720
__PT.POLYTRACK.VIDEO_OUTPUT_SETUP    = False

#Saving output video and graphs
__PT.POLYTRACK.VIDEO_WRITER         = 'DIVX'
__PT.POLYTRACK.SAVE_TRACK_FRAME     = False
__PT.POLYTRACK.SAVE_VIDEO_OUTPUT    = True
__PT.POLYTRACK.PLOT_GRAPH           = False
__PT.POLYTRACK.SIGHTING_TIMES       = False



#Parameters related to changes in reolution(Low res to Hi res)
__PT.POLYTRACK.LR_MODE     = False # Turning off low-res mode when new insect is sighted and reset the hi-res background subtractor
__PT.POLYTRACK.IDLE_OUT    = False # Turning off low-res mode when new insect is sighted
__PT.POLYTRACK.BACKTRACK_FRAMES = 30 #Number of frames to go back when a new insect is detected


#Video parameters
__PT.POLYTRACK.FRAME_WIDTH = 1920
__PT.POLYTRACK.FRAME_HEIGHT = 1080
__PT.POLYTRACK.FPS = 30
__PT.POLYTRACK.FRAME_COUNT= 300

#Tracking related paremeters
__PT.POLYTRACK.EDGE_PIXELS = 40
__PT.POLYTRACK.MAX_OCCLUSIONS = 400 #Threshold number of undetected frames (previously 60)
__PT.POLYTRACK.CLEAR_FRAMES = 0 
__PT.POLYTRACK.CLEAR_FRAMES_THRESH = 5
__PT.POLYTRACK.NOISY = False
__PT.POLYTRACK.MAX_OCCLUSIONS_EDGE = 32
__PT.POLYTRACK.INITIAL_FRAMES = 50 #Tracking will not shift to low resolution during this time
__PT.POLYTRACK.MAX_DIST_BS = 125 #previously 80
__PT.POLYTRACK.MAX_DIST_DL = 300 #previously 240
__PT.POLYTRACK.FLOWER_THRESH_FACTOR = 1.15 #Increase in the radius in factors


__PT.POLYTRACK.INSECT_VERIFICATION = True
__PT.POLYTRACK.INSECT_VERIFICATION_INTERVAL = 60
__PT.POLYTRACK.INSECT_VERIFICATION_MIN_FRAMES = 30
__PT.POLYTRACK.INSECT_VERIFICATION_LAST_FRAMES = 20 #Number of frames to measure distance
__PT.POLYTRACK.INSECT_VERIFICATION_THRESHOLD_CUM_DISTANCE = 20 
__PT.POLYTRACK.INSECT_VERIFICATION_MIN_BS = 0.5 #0.5
__PT.POLYTRACK.NEW_INSECT_MODE = False

__PT.POLYTRACK.DL_DARK_SPOTS = True
__PT.POLYTRACK.DL_DARK_SPOTS_RADIUS = 25
__PT.POLYTRACK.RECORDED_DARK_SPOTS = []

#Saving tracks and filtering
__PT.POLYTRACK.FILTER_TRACKS = False
__PT.POLYTRACK.FILTER_TRACKS_DIST_THRESHOLD = 10
__PT.POLYTRACK.FILTER_TRACKS_VERIFY_FRAMES = 20


#Foreground background detection related parameters
__PT.POLYTRACK.MAX_BG_CHANGES = 50 #20 previosly
__PT.POLYTRACK.MIN_INSECT_AREA = 0 #5
__PT.POLYTRACK.MAX_INSECT_AREA = 7750 #Previosuly 3750

#Analysis Parameters
__PT.POLYTRACK.FACING_NORTH = True # Adjust the recordings based on the direction camera faces (by default the recordings will be facing north)
__PT.POLYTRACK.ANALYSE_POLLINATION = True
__PT.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER = False
__PT.POLYTRACK.ANALYSIS_UPDATE_FREQUENCY = 5 #frames
__PT.POLYTRACK.FLOWER_RADIUS_THRESHOLD = 1.2
__PT.POLYTRACK.UPDATE_FLOWER_ANALYSIS = True #Update the flowers.csv with insect visitation analysis

#Tracking flower movement
__PT.POLYTRACK.FLOWER_UPDATE_FREQUENCY =  10#frames 3000
__PT.POLYTRACK.FLOWER_MOVEMENT_THRESHOLD = 60 #pixels

# Low resolution mode related parameters
__PT.POLYTRACK.LOWERES_FRAME_WIDTH = 852
__PT.POLYTRACK.LOWERES_FRAME_HEIGHT = 480

# Deep Leraning (YOLOv4) related parameters
__PT.POLYTRACK.TRACKING_INSECTS = ['honeybee', 'flower','hoverfly', 'moth']
__PT.POLYTRACK.DL_SCORE_THRESHOLD = 0.5
__PT.POLYTRACK.DL_IOU_THRESHOLD = 0.5
__PT.POLYTRACK.MAX_TOTAL_SIZE = 50
__PT.POLYTRACK.MAX_OUTPUT_SIZE_PER_CLASS = 50
