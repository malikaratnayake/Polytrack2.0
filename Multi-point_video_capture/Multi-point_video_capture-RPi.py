 #!/usr/bin/python

from picamera import PiCamera
from time import sleep
import time
import os
#import board
#import busio
#import adafruit_hts221
#import adafruit_tsl2591



# Initialize the I2C bus.
#i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the light sensor.
#light_sensor = adafruit_tsl2591.TSL2591(i2c)
#Set the gain for the light sensor
#light_sensor.gain = adafruit_tsl2591.GAIN_LOW

# Initialize the HT sensor.
#ht_sensor = adafruit_hts221.HTS221(i2c)



cam_num = 4
 

today_date = int(time.strftime("%Y%m%d"))

statvfs = os.statvfs('/')
free_space = statvfs.f_frsize * statvfs.f_bavail
min_storage = 1


vdo_duration = 600  #record time (sec)
camera = PiCamera()
camera.rotation = 180
camera.resolution = (1920, 1080)
camera.framerate = 30

def measure_temp():
    try:
        temp = os.popen("vcgencmd measure_temp").readline()
        temp_out = (temp.replace("temp=",""))
    except:
        temp_out = 0
        
    return temp_out
    
def measure_hts221():
    try:
        amb_temp = round(ht_sensor.temperature,3)
        rel_hum = round(ht_sensor.relative_humidity,3)
        
    except:
        amb_temp = 0
        rel_hum = 0
        
    return amb_temp, rel_hum
    
def measure_light():
    try:
        _light_inten = round(light_sensor.lux,3)
        _visible_light = light_sensor.visible
        _infrared_light = light_sensor.infrared
        
    except:
        _light_inten = 0
        _visible_light = 0
        _infrared_light = 0
        
    return _light_inten, _visible_light, _infrared_light
    
def get_free_space():
    statvfs = os.statvfs('/')
    free_space = round((statvfs.f_frsize * statvfs.f_bavail)/1000000000,3) #Free space in GB
    return free_space


def create_info_file():
    video_info = open("video/video_info_cam_"+str(cam_num)+".csv", "a")
    video_info.write("Camera Number: "+str(cam_num)+"\nDuration:"+str(vdo_duration)+ " sec \nResolution: "+str(camera.resolution)+ "\nFrameRate: "+str(camera.framerate)+"fps \n")
    video_info.write("File_Num, Date, Time, Ambient_Temp, Relative_Humidity, Light_Intensity(lux),Visble_light,IR_Light, Free_Space (GB), System_Temp \n")
    video_info.close()

def record_info(_video_num):
    current_date = time.strftime("%d/%m/%Y")
    current_time = time.strftime("%H:%M:%S")
    system_temp = measure_temp()
    ambient_temp, relative_humidity = measure_hts221()
    light_inten, visible_light, infrared_light = measure_light()
    free_space= get_free_space()
    
    video_info = open("video/video_info_cam_"+str(cam_num)+".csv", "a")
    video_info.write(str(today_date)+'_'+str(_video_num)+ "," + str(current_date)+ "," + str(current_time)+ "," + str(ambient_temp)+ ","
                     + str(relative_humidity)+ "," + str(light_inten) +  "," + str(visible_light) +  ","+ str(infrared_light) +  ","+ str(free_space)+","+ str(system_temp))
    video_info.close()
    
    print("Video info file updated at: "+str(time.strftime("%c"))+ "\t AT: " + str(ambient_temp)+ "C,  RH: " + str(relative_humidity)+ "%,  LI: " +
          str(light_inten) + "Lux,  Visible: " + str(visible_light)+ "%,  IR: " +  str(infrared_light)+  ",  Free Space: " + str(free_space)+"GB,  ST: " + str(system_temp))


def update_video_list(_video_num):
    video_list = open("video/cam_"+str(cam_num)+"_video_list.txt", "a")
    video_list.write(str(today_date)+'_'+str(_video_num)+", ")
    video_list.close()


    
create_info_file()
record_info(0000)


while True:
    #Record time
    video_num = int(time.strftime("%H%M%S"))
    record_info(video_num)
    update_video_list(video_num)
    #print("Indictor LED ON")

    
    #Record the video
    camera.start_recording('video/cam_'+str(cam_num)+'_video_'+str(today_date)+'_'+str(video_num)+'.h264')
    sleep(vdo_duration)
    camera.stop_recording()

    
    #Calculate Free Storage
    free_space = get_free_space()
    
     
    
    if (free_space<min_storage):
        break

    
        


    


            


