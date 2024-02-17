# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:27:42 2023

@author: cmun
"""


import pyvisa
from pyvisa import constants

import time
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx import stream_readers
import csv
from enum import Enum

import os
import errno

# Datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d%m%Y%H%M")
print("Date and time =", dt_string)	

rm = pyvisa.ResourceManager()

############################# VCSEL-T Source Parameters #########################

visa_VCSELsource='ASRL6::INSTR'  # Nombre del recurso VISA

temp_set = 562                  # [412 612][35 15]  512 -> 25°C, 562 -> 20°C Temperatura [°C] del laser segun formula: ###########
current = 18                    # Corriente del laser [mA] [xx.x]

Vcsel_mode=1                    # Internal Trigger
Frecuencia=16                   # Frecuencia del Internal Trigger

################### Configuracion DAQ    #########################

sample_rate = 16e3                              # Usually sample rate goes 2048 Hz, 2560 Hz, 3200 Hz, 5120 Hz, 6400 Hz (at least for a NI9234 card) 
samples_to_acq = 2**10                           # At least for vibration matters, Samples to acq go from 2048, 4096, 8192
wait_time = samples_to_acq/sample_rate          # Data Acquisition Time in s, very important for the NI task function, and since we have 2048 on both sides, time is 1 s
cont_mode = AcquisitionType.CONTINUOUS              # There is also FINITE for sporadic measurements
iterations = 41

###################################################################

class TerminalConfiguration(Enum):
    RSE = 10083  #: Referenced Single-Ended.
    NRSE = 10078  #: Non-Referenced Single-Ended.
    DIFF = 10106  #: Differential.
    PSEUDO_DIFF = 12529  #: Pseudodifferential.
    DEFAULT = -1  #: Default.

 
def Config_VCSEL_T(Instrumento,Temperatura,VCSEL_SWEEP_Mode,Frequency):
    vcsel_T = rm.open_resource(Instrumento)                 #Inicializa el recurso de la fuente de corriente
    vcsel_T.baud_rate = 9600                               
    vcsel_T.write_termination = '\r\n' #Especificado en el  Datasheet
    vcsel_T.timeout = 25000

    vcsel_T.write("SETT:"+str(int(Temperatura)))   #Establece la temperatura, numero entre #412 a #612 -> 35 a 15
    time.sleep(1)
    vcsel_T.write("SETC:"+str(round(float(0),1))) #Establece la corriente en #xx.xmA 
    time.sleep(1)
    vcsel_T.write("SETM:"+str(int(VCSEL_SWEEP_Mode)))   #Establece modo de barrido #0:DC,   #1:Internal Trigger,   #2:External Trigger
    time.sleep(1)
    vcsel_T.write("SETF:"+str(int(Frequency)))   #Establece la frecuencia del internal trigger #1Hz a #100000Hz

    return vcsel_T


VCSEL_T=Config_VCSEL_T(visa_VCSELsource,temp_set,Vcsel_mode,Frecuencia)
time.sleep(1)
VCSEL_T.write("SETC:"+str(round(float(current),1))) #Establece la corriente en #xx.xmA 

#################### Mediciones ######################################
SSFBG_Temp = []

    ##### Configuracion de la DAQ #####################

with nidaqmx.Task() as task:

        # Two voltage channels
    task.ai_channels.add_ai_voltage_chan("Dev2/ai2",terminal_config=TerminalConfiguration.RSE)   #SSFBG
    task.ai_channels.add_ai_voltage_chan("Dev2/ai1",terminal_config=TerminalConfiguration.RSE)   #Ref
    task.ai_channels.add_ai_voltage_chan("Dev2/ai3",terminal_config=TerminalConfiguration.RSE)   #Trigger
    
    total_wait_time = wait_time * iterations                         # We will only take 10 measurements, 10 s for this example
    samples_to_acq_new = samples_to_acq * iterations                 # Also multiply by 10 to keep the same ratio, it should be 
    
    task.timing.cfg_samp_clk_timing(sample_rate, sample_mode = cont_mode, samps_per_chan = samples_to_acq_new)               


    with open('VCSEL_T_SSFBG_Amplitud_S1R_'+str(sample_rate)+'samples_Temp_'+str(temp_set)+'_Frequency_'+str(Frecuencia)+'_Iterations_'+str(iterations)+'.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(["Muestras de la DAQ", "Tension_SSFBG", "Tension_Referencia","Tension_Trigger","Temperatura_Laser",'Tiempo Total'])
            # writer.writerow(["Tension_SSFBG"])
            # writer.writerow(["Tension_Referencia"])
            # writer.writerow(["Tension_Trigger"])
            # writer.writerow(["Temperatura_SSFBG"])
    
            # adding some blank spaces in btw
            # writer.writerow('')
            # writer.writerow('')        
    
        x = np.linspace(0, total_wait_time, samples_to_acq_new)       # Your x axis (ms), starts from 0, final time is total_wait_time, equally divided by the number of samples you'll capture
                
        data = np.ndarray((3, samples_to_acq_new), dtype = np.float64)  #Creates an array, 4 columns each one of 20480 rows
        start = time.time()

        nidaqmx.stream_readers.AnalogMultiChannelReader(task.in_stream).read_many_sample(data, samples_to_acq_new, timeout = 14) # it should't take that long for this example, check out time for other exercises               
        
        elapsed_time = (time.time() - start)
        print (f'done in {elapsed_time}') 
           
        for value in range(len(x)):
            writer.writerow([x[value], data[0][value], data[1][value], data[2][value],temp_set,elapsed_time])
            

            
        plt.plot(data[0])
        plt.plot(data[1])
        plt.plot(data[2])

        

##### END #####

VCSEL_T.write("SETC:00.0") # Establece la corriente en #xx.xmA 
VCSEL_T.close()


