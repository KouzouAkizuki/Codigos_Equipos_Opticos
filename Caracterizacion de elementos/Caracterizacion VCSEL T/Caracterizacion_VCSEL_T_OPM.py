# -*- coding: utf-8 -*-
"""
Created on Thu Sep  28 10:23:00 2023

@author: Oscar_Riveros & CMUN 
"""

import pyvisa
from pyvisa import constants

import time
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


# Datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%Hh_%Mm")
print("Date and time =", dt_string)	

# Units used for diferent parameters:
#   current: [mA]
#   temperature: [°C]
#   Longitud de onda: [m]
#   Potencia OPM: [W]

############################# VCSEL-T Source Parameters #########################

visa_VCSELsource='ASRL4::INSTR'  # Nombre del recurso VISA

temp_set = 562                  # [412 612][35 15]  512 -> 25°C, 562 -> 20°C Temperatura [°C] del laser segun formula: ###########
current = 17                    # Corriente del laser [mA] [xx.x]

Vcsel_mode=0

Voltage_min = 000               # Tension [V] [0v]
Voltage_max = 999               # Tension [V] [-18v]
Voltage_step=1

############################# OPM parameters #########################

visa_OPM='USB0::0x1313::0x8078::P0025035::INSTR'    #Nombre del recurso VISA

muestras_prom=1

######################################################################

def Config_VCSEL_T(Instrumento,Temperatura,Base_Tension,VCSEL_SWEEP_Mode):
    vcsel_T = rm.open_resource(Instrumento)                 #Inicializa el recurso de la fuente de corriente
    vcsel_T.baud_rate = 9600                               
    vcsel_T.write_termination = '\r\n' #Especificado en el  Datasheet
    vcsel_T.timeout = 25000

    vcsel_T.write("SETT:"+str(int(Temperatura)))   #Establece la temperatura, numero entre #412 a #612 -> 35 a 15
    time.sleep(1)
    vcsel_T.write("SETC:"+str(round(float(0),1))) #Establece la corriente en #xx.xmA 
    time.sleep(1)
    vcsel_T.write("SETDC:"+str(int(Base_Tension)))   #Establece la tension #000 a #999  -> 0v a -20v
    time.sleep(1)
    vcsel_T.write("SETM:"+str(int(VCSEL_SWEEP_Mode)))   #Establece modo de barrido #0:DC,   #1:Internal Trigger,   #2:External Trigger

    return vcsel_T

def Config_OPM_Thorlabs(Instrumento,Muestras_Prom):
    OPM = rm.open_resource(Instrumento)                         #Inicializa el recurso del OPM
    OPM.write("SENS:AVER:COUNT "+str(Muestras_Prom))            #Muestras para el promedio
    print (OPM.query('*IDN?'))                                  #Mensaje de Identificacion del protocolo

    return OPM

def VCSEL_Current_Sweep(Recurso_VCSEL_T,Min_Voltaje,Max_Voltaje,Step_Voltaje,Recurso_OPM,Base_Current):
    Voltaje_Ideal = []                      #Corrientes del barrido
    OPM_power = []                          #Potencia del barrido
    Time = []                               #Tiempo de ejecucion del barrido

    time_ref=time.time()                    #Obtiene el tiempo inicial como referencia
    time_meas=0                             #Variable comodin para obtener el tiempo

    OPMmeas_power=0                         #Variable comodin para obtener el valor numerico de la potencia        
    OPMread_power=0                         #Variable que lee la potencia


    Recurso_VCSEL_T.write("SETDC:"+str(int(Min_Voltaje)))   #Establece la tension #000 a #999  -> 0v a -20v
    time.sleep(1)
    Recurso_VCSEL_T.write("SETC:"+str(round(float(Base_Current),1))) #Establece la corriente en #xx.xmA 

    for i in np.arange(Min_Voltaje,Max_Voltaje,Step_Voltaje):   #Barrido de corriente
        Recurso_VCSEL_T.write("SETDC:"+str(int(i)))   #Establece la tension #000 a #999  -> 0v a -20v
        
        Recurso_OPM.write("*CLS")                                   #Limpia el registro del OPM
        OPMread_power=Recurso_OPM.query("READ?")                    #Lee la potencia optica del OPM
        OPMmeas_power=float(OPMread_power)                          #Obtiene el valor numerico de la potencia optica

        time_meas = time.time() - time_ref                          #Obtiene el tiempo de ejecucion del n paso de corriente

        OPM_power.append(OPMmeas_power)                             #Acumula la lista de potencia
        Time.append(time_meas)                                      #Acumula la lista de tiempo
        Voltaje_Ideal.append(i)                                     #Acumula la lista de corriente ideal

    Recurso_VCSEL_T.write("SETC:"+str(round(float(0),1))) #Establece la corriente en #xx.xmA 

    return Time,Voltaje_Ideal,OPM_power


rm = pyvisa.ResourceManager()

###### Configuracion de la fuente de corriente de Thorlabs
VCSEL_T=Config_VCSEL_T(visa_VCSELsource,temp_set,Voltage_min,Vcsel_mode)

###### Configuracion del medidor de potencia optica
OPM=Config_OPM_Thorlabs(visa_OPM,muestras_prom)

###### Mediciones 
Tiempo,Voltaje_Barrido,Potencia=VCSEL_Current_Sweep(VCSEL_T,Voltage_min,Voltage_max,Voltage_step,OPM,current)
     
###### End ######
OPM.close()
VCSEL_T.close()

####################### Data to .csv ##########################
filename = "VCSEL_1550_T_Caracterizacion_"+dt_string+"_Temp_"+str(temp_set)+"_Voltaje_Step_"+str(Voltage_step)+"_OPM_OSA_.csv"
file = open(filename,"w")
file.write("Time,Voltaje_Ideal,Power\n")
for s in range(len(Tiempo)-1):
    file.write(str(Tiempo[s])+","+str(Voltaje_Barrido[s])+","+str(Potencia[s])+"\n")
file.close()

####################### Plotting ##########################
plt.plot(Voltaje_Barrido, Potencia)
plt.show()





