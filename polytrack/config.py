#! /usr/bin/env python
# coding=utf-8
from easydict import EasyDict as edict


__PT                           = edict()
# Consumers can get config by: from config import cfg

pt_cfg                           = __PT

# POLYTRACK options
__PT.POLYTRACK                 = edict()

__PT.POLYTRACK.INPUT          = './data/video/video_24_2.mp4' # File location of the input video file (If only a single video needs to be processed)
__PT.POLYTRACK.INPUT_DIR      = './data/video/' # Specify the directory of the input video files 
# __PT.POLYTRACK.INPUT_DIR      = '/home/mrat0006/bm75_scratch/Sunny_Ridge_March2021/15March2021/Cam_2/converted/'
#__PT.POLYTRACK.INPUT_DIR      = '/home/mrat0006/bm75/Polytrack/data/video/'
__PT.POLYTRACK.VIDEO_EXT      = 'avi' # Video type
__PT.POLYTRACK.CONTINUOUS_VIDEO = True # For processing multiple video files - TRUE, if video files are sequencial
__PT.POLYTRACK.OUTPUT         = './data/output/' # Output directory
__PT.POLYTRACK.VIDEO_START_TIME = None #Start time of the video. To be extracted from the video file name (defaul setting -> None)
__PT.POLYTRACK.CURRENT_VIDEO_DETAILS = None #Video details. To be extracted from the video file name (defaul setting -> None)
__PT.POLYTRACK.INSECT_COUNT = 0 

#Displaying output video
__PT.POLYTRACK.SHOW_TRACK_FRAME      = False # Set TRUE to display insect tracks in a seperate window.
__PT.POLYTRACK.SHOW_VIDEO_OUTPUT     = True # Set TRUE to display output video. Insect tracks superimposed on the video.
__PT.POLYTRACK.VIDEO_OUTPUT_WIDTH    = 1280 # Width of the output frame.
__PT.POLYTRACK.VIDEO_OUTPUT_HEIGHT   = 720 # Height of the output frame.
__PT.POLYTRACK.VIDEO_OUTPUT_SETUP    = False # Initialisation parameter

#Saving output video and graphs
__PT.POLYTRACK.VIDEO_WRITER         = 'DIVX' #Set the video writer
__PT.POLYTRACK.SAVE_TRACK_FRAME     = False #Set TRUE to record a video with insect tracks
__PT.POLYTRACK.SAVE_VIDEO_OUTPUT    = False #Set TRUE to record output video
__PT.POLYTRACK.PLOT_GRAPH           = False #Set TRUE to save the insect trajectories as PNGs
__PT.POLYTRACK.SIGHTING_TIMES       = False #Set TRUE to export a csv with insect sighting times



#Parameters related to changes in reolution(Low res to Hi res)
__PT.POLYTRACK.LR_MODE     = False # Set TRUE to process the videos in low resolution when insects are not being tracked 
__PT.POLYTRACK.IDLE_OUT    = False # Set to default value FALSE
__PT.POLYTRACK.BACKTRACK_FRAMES = 30 # Number of frames to go back when a new insect is detected while in the low resolution mode
# (Backtrack frames option is used to provide the background subtractor with adaquate no. of frames to build a model of the background)


#Video parameters
__PT.POLYTRACK.FRAME_WIDTH = 1920 # Width of the input video
__PT.POLYTRACK.FRAME_HEIGHT = 1080 # Height of the input video
__PT.POLYTRACK.FPS = 30 # Framerate of the input video
__PT.POLYTRACK.FRAME_COUNT= 300 # Automatically updated by the algorithm.

#Tracking related paremeters
__PT.POLYTRACK.EDGE_PIXELS = 40 # Defines the thickness of the border of the video. If an insect disappears outside the border, Polytrack considers the insect has left the frame. 
__PT.POLYTRACK.MAX_OCCLUSIONS = 60 #Threshold number of undetected frames (previously 60). Polytrack considers an insect has left the frame if it has not been detected for a consecutive MAX_OCCLUSIONS frame.
__PT.POLYTRACK.CLEAR_FRAMES = 0 # Automatically updated by the algorithm.
__PT.POLYTRACK.CLEAR_FRAMES_THRESH = 5 # Maximum number of insect-like foreground changes allowed for use of background subtraction (If no of changes > threshold; YOLOv4 will be used for the detection/verification)
__PT.POLYTRACK.NOISY = False # Automatically updated by the algorithm.
__PT.POLYTRACK.MAX_OCCLUSIONS_EDGE = 32 # Threshold number of undetected frames allowed at the edge. Polytrack considers an insect has left the frame if it has not been detected for a consecutive MAX_OCCLUSIONS_EDGE frame.
__PT.POLYTRACK.INITIAL_FRAMES = 50 #Tracking will not shift to low resolution during this time
__PT.POLYTRACK.MAX_DIST_BS = 125 #Max distance allowed between predicted position and background subtraction-based detection for association (Please refer https://doi.org/10.1371/journal.pone.0239504 for more information)
__PT.POLYTRACK.MAX_DIST_DL = 300 #Max distance allowed between predicted position and deep learning-based detection for association (Please refer https://doi.org/10.1371/journal.pone.0239504 for more information)
__PT.POLYTRACK.FLOWER_THRESH_FACTOR = 1.15 # Width of the flower border (for marking flowers in the video output)


__PT.POLYTRACK.INSECT_VERIFICATION = True #Verify insect track for false positives while tracking.
__PT.POLYTRACK.INSECT_VERIFICATION_INTERVAL = 60 #Interval between two verifications
__PT.POLYTRACK.INSECT_VERIFICATION_MIN_FRAMES = 30 #Minimum recorded duration of the track that is considered for the verification.
__PT.POLYTRACK.INSECT_VERIFICATION_LAST_FRAMES = 20 #Number of frames to measure distance
__PT.POLYTRACK.INSECT_VERIFICATION_THRESHOLD_CUM_DISTANCE = 20 # Minimum total distance the track must have recorded to qualify as a verfied (true positive) track.
__PT.POLYTRACK.INSECT_VERIFICATION_MIN_BS = 0.5 #Minimum number of background subtraction based detections a track should contain to bypass the verification process. 
__PT.POLYTRACK.NEW_INSECT_MODE = False # Automatically updated by the algorithm.

__PT.POLYTRACK.DL_DARK_SPOTS = True # Mark the positions of false positive YOLO detections for later reference
__PT.POLYTRACK.DL_DARK_SPOTS_RADIUS = 25 # The concering radius around the false positive YOLO detection. 
__PT.POLYTRACK.RECORDED_DARK_SPOTS = [] # Automatically updated by the algorithm.

#Saving tracks and filtering
__PT.POLYTRACK.FILTER_TRACKS = False # Filter tracks for False positives prior to saving.
__PT.POLYTRACK.FILTER_TRACKS_DIST_THRESHOLD = 10 #Minimum total distance of the track reuired for verification as a True Positive
__PT.POLYTRACK.FILTER_TRACKS_VERIFY_FRAMES = 20 # Number of frames considered for the verification process.


#Foreground background detection related parameters
__PT.POLYTRACK.MAX_BG_CHANGES = 50 # Maximum number of foreground changes (blobs) allowed. (If actual FG changes > Max value; YOLO will be used for the detection)
__PT.POLYTRACK.MIN_INSECT_AREA = 2 # Minimum area covered by an insect (pixels)
__PT.POLYTRACK.MAX_INSECT_AREA = 4750 # Maximum area covered by an insect (pixels)

#Analysis Parameters
__PT.POLYTRACK.FACING_NORTH = True # Adjust the recordings based on the direction camera faces (by default the recordings will be facing north)
__PT.POLYTRACK.ANALYSE_POLLINATION = True #Set TRUE to monitor insect flower visits for pollination analysis
__PT.POLYTRACK.RECORD_ENTRY_EXIT_FLOWER = False # Set TRUE to record insect extry and exit points in a flower
__PT.POLYTRACK.ANALYSIS_UPDATE_FREQUENCY = 5 # Interval for updating the analysis
__PT.POLYTRACK.FLOWER_RADIUS_THRESHOLD = 1.2 # Additional area to be considered when monitoring flower visits. 
__PT.POLYTRACK.UPDATE_FLOWER_ANALYSIS = True #Update the flowers.csv with insect visitation analysis

#Tracking flower movement
__PT.POLYTRACK.FLOWER_UPDATE_FREQUENCY =  1000 # Interval (frames) for updating the flower position
__PT.POLYTRACK.FLOWER_MOVEMENT_THRESHOLD = 60 # Maximum distance a flower can move during the update interval. Flower detections beyond this threshold are considered as newly detected flowers.

# Low resolution mode related parameters
__PT.POLYTRACK.LOWERES_FRAME_WIDTH = 852 #Frame width for the low resolution processing mode
__PT.POLYTRACK.LOWERES_FRAME_HEIGHT = 480 # Frame height for the low resolution processing mode

# Deep Leraning (YOLOv4) related parameters
__PT.POLYTRACK.TRACKING_INSECTS = ['honeybee', 'flower','hoverfly', 'moth'] #Class labels
__PT.POLYTRACK.DL_SCORE_THRESHOLD = 0.3 # Minimum confidence for a detection
__PT.POLYTRACK.DL_IOU_THRESHOLD = 0.3 # IoU for a detection
__PT.POLYTRACK.MAX_TOTAL_SIZE = 50 # Maximum number of detections per frame
__PT.POLYTRACK.MAX_OUTPUT_SIZE_PER_CLASS = 50 
