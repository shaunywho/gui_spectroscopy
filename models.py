import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
import cv2
import csv
# from datatime import datetime
import time
import os
import pandas as pd 
from collections import deque

class Camera:
    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.last_frame = np.zeros((1,1))
        self.video_on = False

    def initialise(self):
        self.cap = cv2.VideoCapture(self.cam_num)

    def get_frame(self):
        ret, frame = self.cap.read()
        self.last_frame = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),1)
        return self.last_frame


    def set_brightness(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def get_brightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)


    def close_camera(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)

class DAQ:
    def __init__(self):
        self.ai_task = nidaqmx.Task()
        self.ao_task = nidaqmx.Task()
        self.ai_task.ai_channels.add_ai_voltage_chan("cDAQ1Mod1/ai0")
        self.ao_task.ao_channels.add_ao_voltage_chan("cDAQ1Mod2/ao0", min_val=0, max_val=5.0)
        self.ai_task.timing.cfg_samp_clk_timing(rate=1000,
                                    sample_mode=AcquisitionType.CONTINUOUS,samps_per_chan= 1000)
        self.ao_task.timing.cfg_samp_clk_timing(rate=1000,sample_mode=AcquisitionType.CONTINUOUS,samps_per_chan= 1000,source='/DAQ/ai/SampleClock')
        self.delay = 0

        self.number_of_samples = 1000
        self.sampling_rate = 1000

    def read_data(self):
        self.data = np.array(self.ai_task.read(number_of_samples_per_channel=self.number_of_samples))
        self.time = np.linspace(0,self.number_of_samples/self.sampling_rate,self.number_of_samples)
        return self.data, self.time

    def save_data(self,save_time):
        directory = os.path.join(os.getcwd(),save_time)
        if not os.path.exists(directory):

            os.mkdir(directory)
        i=0
        while os.path.exists(os.path.join(directory,f"test{i}.csv")):
            i+=1
        filepath = os.path.join(directory,f"test{i}.csv")
        df = pd.DataFrame({"Data":self.data, "Time":self.time})
        df.to_csv(filepath)



    def set_config(self):
        self.ai_task.timing.cfg_samp_clk_timing(rate = self.sampling_rate,samps_per_chan=self.number_of_samples, sample_mode=AcquisitionType.CONTINUOUS)
        self.ao_task.timing.cfg_samp_clk_timing(rate = self.sampling_rate,samps_per_chan=self.number_of_samples, sample_mode=AcquisitionType.CONTINUOUS,source='/DAQ/ai/SampleClock')
        ramp_fn = np.linspace(0,.02, self.number_of_samples)
        self.ao_task.write(ramp_fn)

    def start_measurement(self):
        self.set_config()
        self.ao_task.start()

    def stop_measurement(self):
        self.ai_task.stop()
        self.ao_task.stop()
    def close_daq(self):
        self.stop_measurement()
        self.ai_task.close()
if __name__ == '__main__':
    cam = Camera(0)
    cam.initialise()
    print(cam)
    frame = cam.get_frame()
    print(frame)
    cam.set_brightness(1)
    print(cam.get_brightness())
    cam.set_brightness(0.5)
    print(cam.get_brightness())
    cam.close_camera()