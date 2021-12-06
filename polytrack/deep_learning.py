import os
import time
import cv2
import random
import colorsys
import numpy as np
import tensorflow as tf
import pytesseract
import core.utils as utils
from core.config import cfg
import re
from PIL import Image
from polytrack.general import cal_dist
import itertools as it
import math

# import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
tf.config.set_visible_devices(physical_devices[0:1], 'GPU')
from absl import app, flags, logging
from absl.flags import FLAGS
import core.utils as utils
from core.yolov4 import filter_boxes

from tensorflow.python.saved_model import tag_constants
from PIL import Image
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from polytrack.config import pt_cfg


model_weights = './checkpoints/custom-416'
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
saved_model_loaded = tf.saved_model.load(model_weights, tags=[tag_constants.SERVING])
infer = saved_model_loaded.signatures['serving_default']



def dl_detections_process(bboxes):
    classes = utils.read_class_names(cfg.YOLO.CLASSES)
    allowed_classes = pt_cfg.POLYTRACK.TRACKING_INSECTS
    num_classes = len(classes)
    _dl_detections = np.zeros(shape=(0,6)) 
    out_boxes, out_scores, out_classes, num_boxes = bboxes
    for i in range(num_boxes):
        if int(out_classes[i]) < 0 or int(out_classes[i]) > num_classes: continue
        coor = out_boxes[i]
        score = out_scores[i]
        class_ind = int(out_classes[i])
        # print(class_ind, classes[class_ind])
        class_name = classes[class_ind]

        if class_name not in allowed_classes:
            continue
        else:
            _dl_detections = np.vstack([_dl_detections,(coor[0], coor[1], coor[2], coor[3], class_name, score)])

    return _dl_detections


def map_darkspots(__frame, _dark_spots):
    for spot in _dark_spots:
        __frame = cv2.circle(__frame, (int(spot[0]), int(spot[1])), int(pt_cfg.POLYTRACK.DL_DARK_SPOTS_RADIUS), (100,100,100), -1)

    return __frame



def run_DL(_frame):

    #if pt_cfg.POLYTRACK.DL_DARK_SPOTS: 
        #dark_spots = pt_cfg.POLYTRACK.RECORDED_DARK_SPOTS
        #if len(dark_spots): 
           # _frame = map_darkspots(_frame, dark_spots)
        #else:
          #  pass
  #  else:
     #   pass

    _frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(_frame)

    frame_size = _frame.shape[:2]
    image_data = cv2.resize(_frame, (cfg.YOLO.INPUT_SIZE, cfg.YOLO.INPUT_SIZE))
    image_data = image_data / 255.
    image_data = image_data[np.newaxis, ...].astype(np.float32)
    

    batch_data = tf.constant(image_data)
    pred_bbox = infer(batch_data)
    for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]

    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=pt_cfg.POLYTRACK.MAX_OUTPUT_SIZE_PER_CLASS,
        max_total_size=pt_cfg.POLYTRACK.MAX_TOTAL_SIZE,
        iou_threshold=pt_cfg.POLYTRACK.DL_IOU_THRESHOLD,
        score_threshold=pt_cfg.POLYTRACK.DL_SCORE_THRESHOLD
    )

    # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
    original_h, original_w, _ = _frame.shape
    bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)

    pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

    # read in all class names from config
    class_names = utils.read_class_names(cfg.YOLO.CLASSES)

    _detections = dl_detections_process(pred_bbox)

    return _detections

    #Calculate the area covered by the insect
def cal_bodyArea_DL(_x_TL,_y_TL,_x_BR,_y_BR): 
    _body_area = abs((_x_BR-_x_TL)*(_y_BR-_y_TL))
    
    return _body_area


#Extract the data from result and calculate the center of gravity of the insect
def cal_CoG_DL(result): 
    _x_DL, _y_DL, _body_area, _radius  = 0, 0, 0, 0
    _x_TL  = int(float(result[0]))
    _y_TL = int(float(result[1]))
    _x_BR = int(float(result[2]))
    _y_BR = int(float(result[3]))
    _x_DL = int(round((_x_TL+_x_BR)/2))
    _y_DL = int(round((_y_TL+_y_BR)/2))


    
    _radius = round(cal_dist(_x_TL, _y_TL,_x_DL,_y_DL)*math.cos(math.radians(45)))
    
    _body_area = cal_bodyArea_DL(_x_TL,_y_TL,_x_BR,_y_BR)

    return _x_DL,_y_DL, _body_area, _radius


#Detect insects in frame using Deep Learning
def detect_deep_learning(_frame, flowers = False):
    _results = run_DL(_frame)
    #print(flowers)

    _deep_learning_detections = process_DL_results(_results, flowers)

    if (len(_deep_learning_detections)>1) : 
        _deep_learning_detections = verify_insects_DL(_deep_learning_detections)
    else:
        pass


    return _deep_learning_detections
    


def process_DL_results(_results, flowers):
    _logDL = np.zeros(shape=(0,5)) #(create an array to store data x,y,area, conf, type)

    for result in _results: # Go through the detected results
        confidence = result[5]
        _species = result[4]

        if not flowers:
            if ((_species != 'flower')): # Filter out detections which do not meet the threshold
                _x_DL, _y_DL, _body_area, _ = cal_CoG_DL(result) #Calculate the center of gravity
                
                _logDL = np.vstack([_logDL,(float(_x_DL), float(_y_DL), float(_body_area),_species,confidence)])
                
            else:
                pass
        else:
            if ((_species == 'flower')): # Filter out detections which do not meet the threshold
                _x_DL, _y_DL, _ , _radius = cal_CoG_DL(result) #Calculate the center of gravity
                
                _logDL = np.vstack([_logDL,(float(_x_DL), float(_y_DL), float(_radius),_species,confidence)])
            
            else:
                pass
                   
    
    return _logDL


# Calculate the distance between two coordinates
def cal_euclidean_DL(_insects_inFrame,_pair):
    _dx = float(_insects_inFrame[_pair[0]][0]) - float(_insects_inFrame[_pair[1]][0])
    _dy = float(_insects_inFrame[_pair[0]][1]) - float(_insects_inFrame[_pair[1]][1])
    _dist = np.sqrt(_dx**2+_dy**2)
    
    return _dist   

#Verify that there are no duplicate detections (The distance between two CoG are >= 20 pixels)
def verify_insects_DL(_insects_inFrame):
    _conflict_pairs = []
    _combinations = it.combinations(np.arange(len(_insects_inFrame)), 2)
    
    for pair in _combinations:
        _distance = cal_euclidean_DL(_insects_inFrame,pair)
        if (_distance<15):
            _conflict_pairs.append(pair)

    if (_conflict_pairs): _insects_inFrame = evaluvate_conflict(_conflict_pairs, _insects_inFrame)
    
    return _insects_inFrame

#Evaluvate the confidence levels in DL and remove the least confidence detections
def evaluvate_conflict(_conflict_pairs, _insects_inFrame):
    to_be_removed = []
    for pairs in _conflict_pairs:
        conf_0 = _insects_inFrame[pairs[0]][4]
        conf_1 = _insects_inFrame[pairs[1]][4]
        
        if (conf_0>=conf_1):to_be_removed.append(pairs[1])
      
        else: to_be_removed.append(pairs[0])
    
    to_be_removed = list(dict.fromkeys(to_be_removed)) #Remove duplicates
    _insects_inFrame = np.delete(_insects_inFrame, to_be_removed, 0)

    return _insects_inFrame
