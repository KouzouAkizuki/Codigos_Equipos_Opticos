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

############################# Thorlabs ITC8000 Source Parameters #########################

visa_Isource='ASRL3::INSTR'    #Nombre del recurso VISA

slot = 1                        #Ranura del Laser
temp_start = 20                 #Temperatura inicial del Laser  [°C]
temp_tol = 0.1                  #Tolerancia de temperatura del Laser    [°C]
tec_current_limit_sw=0.7        #Limite de corriente del TEC del Laser  [A]

current_limit_SW = 0.012        #Limite de corriente del laser  [A]
source_operation_mode = "CC"    #CC: constant current; CP: constant Power   
ldpol="CG"                      #Polarizacion del Laser
pdpol="AG"                      #Polarizacion del fotodiodo del Laser


Pshare=40                       #Constante proporcional del PID de temperatura
Dshare=8                        #Constante derivativa del PID de temperatura
Ishare=30                       #Constante integrativa del PID de temperatura
Ishare_Status='ON'              #Activacion de la constante integrativa

current_min  = 70e-6            #Corriente inicial del Laser[A]
current_max  = 0.012            #Corriente final del Laser[A]
current_step = 70e-6            #Paso de corriente del Laser[A]


slot_mount=2                    #Ranura de la montura
temp_start_mount = 20           #Temperatura inicial de la Montura
temp_tol_mount = 0.1              #Tolerancia de temperatura de la Montura
tec_current_limit_sw_mount=2    #Limite de corriente del TEC de la Montura

Pshare_mount=100                #Constante proporcional del PID de temperatura para la montura
Dshare_mount=2.5                #Constante derivativa del PID de temperatura para la montura
Ishare_mount=10                 #Constante integrativa del PID de temperatura para la montura
Ishare_Status_mount='ON'        #Activacion de la constante integrativa para la montura



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


def Config_MOUNT_Thorlabs(Recurso_Isource,Slot,Tec_Current_Limit,PSHARE,DSHARE,ISHARE,ISHARE_Status):
    Recurso_Isource.write(':SLOT '+str(Slot))                      #Seleccion del canal de la fuente
    Recurso_Isource.write(":LIMT:SET "+str(Tec_Current_Limit))     #Establecer limite de corriente del TEC
    Recurso_Isource.write(":SHAREP:SET "+str(PSHARE))              #Establecer la constante proporcional del control PID de la temperatura
    Recurso_Isource.write(":SHARED:SET "+str(DSHARE))              #Establecer la constante derivativa del control PID de la temperatura
    Recurso_Isource.write(":SHAREI:SET "+str(ISHARE))              #Establecer la constante integrativa del control PID de la temperatura
    Recurso_Isource.write(":INTEG "+ISHARE_Status)                 #Enciende la constante integrativa del control PID de la temperatura

    Recurso_Isource.write(':TEC OFF')                               #Apaga el TEC

    print('Mount_Slot'+Isource.query(":SLOT?"))             #Slot de la montura
    print('TEC_Limit'+Isource.query(":LIMT:SET?"))          #Limite de corriente del TEC de la montura
    print('TEC'+Isource.query(":TEC?"))                     #Estado del TEC
    print('Pshare'+Isource.query(":SHAREP:SET?"))           #Valor de la constante Proporcional del PID de la montura
    print('Dshare'+Isource.query(":SHARED:SET?"))           #Valor de la constante derivativa del PID  de la montura
    print('Ishare'+Isource.query(":SHAREI:SET?"))           #Valor de la constante integrativa del PID  de la montura
    print('Ishare_Status'+Isource.query(":INTEG?"))         #Estado de la constante integrativa del PID  de la montura


def Config_VCSEL_Thorlabs(Instrumento,Slot_VCSEL,Operation_Mode,Tec_Current_Limit,Laser_Current_Limit,LDPOL,PDPOL,PSHARE,DSHARE,ISHARE,ISHARE_Status):
    Isource = rm.open_resource(Instrumento)                 #Inicializa el recurso de la fuente de corriente
    Isource.baud_rate = 19200                               
    Isource.set_visa_attribute(constants.VI_ATTR_ASRL_FLOW_CNTRL, constants.VI_ASRL_FLOW_RTS_CTS)   
    Isource.break_lenght = 256                              
    Isource.timeout = 5000
    print (Isource.query('*IDN?'))                          #Mensaje de Identificacion del protocolo

    Isource.write(':SLOT '+str(Slot_VCSEL))                 #Seleccion del canal de la fuente
    Isource.write(':MODE '+Operation_Mode)                  #Operacion de la fuente de corriente
    Isource.write(":LIMT:SET "+str(Tec_Current_Limit))      #Establecer limite de corriente del TEC
    Isource.write(":LIMC:SET "+str(Laser_Current_Limit))    #Establecer limite de corriente del laser
    Isource.write(":LDPOL "+LDPOL)                          #Establecer limite de corriente del laser
    Isource.write(":PDPOL "+PDPOL)                          #Establecer limite de corriente del laser
    Isource.write(":SHAREP:SET "+str(PSHARE))               #Establecer la constante proporcional del control PID de la temperatura
    Isource.write(":SHARED:SET "+str(DSHARE))               #Establecer la constante derivativa del control PID de la temperatura
    Isource.write(":SHAREI:SET "+str(ISHARE))               #Establecer la constante integrativa del control PID de la temperatura
    Isource.write(":INTEG "+ISHARE_Status)                  #Enciende la constante integrativa del control PID de la temperatura

    Isource.write(':TEC OFF')                               #Apaga el TEC
    Isource.write(":LASER OFF")                             #Apaga el Laser

    print('VCSEL_Slot'+Isource.query(":SLOT?"))             #Slot del VCSEL
    print('POL_LASER'+Isource.query(':LDPOL?'))             #Polarizacion del laser
    print('POL_PHOTO'+Isource.query(':PDPOL?'))             #Polarizacion del fotodetector
    print('TEC_Limit'+Isource.query(":LIMT:SET?"))          #Limite de corriente del TEC
    print('Laser_Limit'+Isource.query(":LIMC:SET?"))        #Limite de corriente del Laser
    print('OP_Mode'+Isource.query(":MODE?"))                #Modo de operacion del laser
    print('TEC'+Isource.query(":TEC?"))                     #Estado del TEC
    print('LASER'+Isource.query(":LASER?"))                 #Estado del LASER
    print('Pshare'+Isource.query(":SHAREP:SET?"))           #Valor de la constante Proporcional del PID
    print('Dshare'+Isource.query(":SHARED:SET?"))           #Valor de la constante derivativa del PID
    print('Ishare'+Isource.query(":SHAREI:SET?"))           #Valor de la constante integrativa del PID
    print('Ishare_Status'+Isource.query(":INTEG?"))         #Estado de la constante integrativa del PID


    return Isource

def Basic_Temp_Set(Recurso_Isource,Temperatura,Tolerancia):
    Recurso_Isource.write("*CLS")                                  #Limpia la memoria de la fuente Thorlabs
    Recurso_Isource.write(":TEMP:SET "+str(float(Temperatura)))    #Coloca una temperatura en la fuente
    Recurso_Isource.write(':TEC ON')                               #Prende el TEC de la fuente

    txt = Recurso_Isource.query(":TEMP:ACT?")                      #Pregunta la temperatura a la fuente
    temp_ac = txt.split(" ")                                                
    temp_ac = float(temp_ac[1])                                     #Obtiene el valor de temperatura

    while (abs(Temperatura - temp_ac) > Tolerancia):                #Ciclo hasta que la diferencia de temperatura sea +- Tolerancia°C
        txt = Recurso_Isource.query(":TEMP:ACT?")                   #Pregunta la temperatura
        temp_ac = txt.split(" ")
        temp_ac = float(temp_ac[1])                                 
        print("temp: "+ str(temp_ac))


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

Isource=Config_VCSEL_Thorlabs(visa_Isource,slot,source_operation_mode,tec_current_limit_sw,current_limit_SW,ldpol,pdpol,Pshare,Dshare,Ishare,Ishare_Status)
Config_MOUNT_Thorlabs(Isource,slot_mount,tec_current_limit_sw_mount,Pshare_mount,Dshare_mount,Ishare_mount,Ishare_Status_mount)

Isource.write(':SLOT '+str(slot_mount))                      #Seleccion del canal de la fuente para la montura
Basic_Temp_Set(Isource,temp_start_mount,temp_tol_mount)
Basic_Temp_Set(Isource,temp_start_mount,temp_tol_mount)             
Basic_Temp_Set(Isource,temp_start_mount,temp_tol_mount)             
Basic_Temp_Set(Isource,temp_start_mount,temp_tol_mount)             #Cuarta verificacion por si existen sobrepicos


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


    with open('VCSEL_T_SSFBG_Amplitud_S1R_'+str(sample_rate)+'samples_Temp_'+str(temp_set)+'_Frequency_'+str(Frecuencia)+'_Iterations_'+str(iterations)+'_Temp_Mount_'+str(temp_start_mount)+'.csv', 'w', newline = '') as f:
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

Isource.write(':SLOT '+str(slot_mount))         #Seleccion del canal de la montura
Isource.write(":LASER OFF")                     #Apaga el Laser
Isource.write(':TEC OFF')                       #Apaga el TEC  

Isource.close()
VCSEL_T.write("SETC:00.0") # Establece la corriente en #xx.xmA 
VCSEL_T.close()


