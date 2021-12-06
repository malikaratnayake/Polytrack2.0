# Polytrack 2.0

## Introduction

Polytrack 2.0 is designed to track multiple species of insect pollinators in complex dynamic environments and to monitor their pollination behaviour. It uses a combination of foreground-background segmentation (KNN background subtractor) and deep learning-based detection (YOLOv4) for tracking. Polytrack is capable of indentifying and recording insect-flower interactions for pollination monitoring.  

## Dependencies

Dependencies related to this code is provided in requirements-cpu.txt and requirements-gpu.txt files.

## Pre-trained weights for YOLOv4

Pre-trained weights for YOLOv4 can be downloaded from [here](https://drive.google.com/drive/folders/1FbIh9ZAb5eV53zGvzFXdAHyblrfxmj6-?usp=sharing). 

Rename the weights file to custom.weights and copy and paste it into the "data" folder of this repository.

Use the following commands to convert the darkflow weights to Tensorflow. The pre-trained weights were trained on honeybee and strawberry flower images. Please make sure "./data/classes/custom.name" file contains the correct names of the classes (i.e. honeybee and flower)
 
```
python save_model.py --weights ./data/custom.weights --output ./checkpoints/custom-416 --input_size 416 --model yolov4 
```

## Running the software

Code related to the core functionality of the Polytrack algorithm is in the folder "polytrack" of this repository.

Tracking parameters and working derectories of the code can be specified in the file "./polytrack/config.py". The user has the option of specifying a single input video or collection of videos. Descriptions related to the tracking parameters are defined alongside the parameter value.

After declaring relevant parameters, navigate to the root folder of the repository and run use the following command to run Polytrack.
```
python PolyTrack.py 
```

## Output

Polytrack will output following files related to tracking. The optput directory can be in the config file.

* Insect movement tracks with flower visit information (One track per each detected insect).
* Snapshot of detected insects (For species verfication, if required).
* Flower tracks.
* Final position of flowers (For visualisations).

In addition to the above metioned files, user can select the option to output the tracking video in the config file. This will output a video that contains only the instances where an insect being tracked. 



## Contact

If there are any inquiries, please don't hesitate to contact me at Malika DOT Ratnayake AT monash DOT edu.
 
## References
 
The YOLOv4 component of this repository was adopted from [darknet repository](https://github.com/AlexeyAB/darknet) by AlexeyAB and [yolov4-custom-functions](https://github.com/theAIGuysCode/yolov4-custom-functions) by the AIGuysCode.
