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

visa_VSELsource='ASRL3::INSTR'  # Nombre del recurso VISA

temp_set = 512                  # Temperatura [°C] del laser segun formula: ###########
current = 18                    # Corriente del laser [mA]

Vcsel_mode=0

Voltage_min = 000               # Tension [V] del laser segun la formula: ##########
Voltage_max = 999               # Tension [V] del laser segun la formula: ##########
Voltage_step=1

############################# OSA parameters #########################

visa_OSA ='ASRL5::INSTR'    #Nombre del recurso VISA

OSA_display = "ON"          #Enciente/Apaga el display del OSA
fiber_conector = "ANGLED"   #Tipo de fibra

wavelength_center = 1550    #Longitud de onda central   [nm]
wavelength_span = 7        #Span de medicion   [nm]  ->  Lamda +- SPAN   

osa_resolution = 20         #Resolucion de medicion del OSA [pm]
osa_sensitivity = "MID"     #Sensibilidad del OSA

level_offset = 0            #Offset de potencia del osa [dBm]
level_ref = -15              #Nivel de referencia de potencia [dBm]

sweep_mode = " SINGLE"      #Tipo de medicion
sweep_speed = "2x"          #Velocidad de medicion

############################# OPM parameters #########################

visa_OPM='USB0::0x1313::0x8078::P0023445::INSTR'    #Nombre del recurso VISA

muestras_prom=1

############################# Parametros del Experimento #########################

Repeticiones=10

######################################################################

def Config_VCSEL_T(Instrumento,Temperatura,Base_Tension,VCSEL_SWEEP_Mode):
    vcsel_T = rm.open_resource(Instrumento)                 #Inicializa el recurso de la fuente de corriente
    vcsel_T.baud_rate = 9600                               
    vcsel_T.write_termination = '\r\n' #Especificado en el  Datasheet
    vcsel_T.timeout = 25000

    vcsel_T.write("SETT:"+str(int(Temperatura)))   #Establece la temperatura, numero entre #412 a #612 -> 35 a 15
    vcsel_T.write("SETC:"+str(round(float(0),1))) #Establece la corriente en #xx.xmA 
    vcsel_T.write("SETDC:"+str(int(Base_Tension)))   #Establece la tension #000 a #999  -> 0v a -20v
    vcsel_T.write("SETM:"+str(int(VCSEL_SWEEP_Mode)))   #Establece modo de barrido #0:DC,   #1:Internal Trigger,   #2:External Trigger

    return vcsel_T

def Config_OSA_Yokogawa(Instrumento,Display_Status,Wavelength_Center,Wavelength_Span,Osa_Resolution,OSA_Sensitivity,Level_Offset,Level_Ref,Sweep_Mode,Sweep_Speed):
    OSA = rm.open_resource(Instrumento)                         #Inicializa el recurso del OSA
    OSA.timeout = 5000
    print (OSA.query('*IDN?'))                                  #Mensaje de Identificacion del protocolo

    OSA.write("*RST")
    # clear the output buffer
    try:
        OSA.query("")
    except:
        pass

    OSA.write(":DISP "+Display_Status)                                  #Especifica que el display esta encendido
    OSA.write(":SENSE:WAV:CENT "+str(Wavelength_Center)+"NM")           #Configura una longitud de onda central
    OSA.write(":SENSE:WAV:SPAN "+str(Wavelength_Span)+"NM")             #Configura el span del OSA
    OSA.write(":SENSE:BWID:RES "+str(Osa_Resolution)+"PM")              #Configura la resolucion del OSA
    OSA.write(":SENSE:SENSE "+OSA_Sensitivity)                          #Configura la sensibilidad del OSA
    OSA.write(":SENSE:SWEEP:POINTS:AUTO ON")                            #Establece la cantidad de puntos automaticamente
    OSA.write(":SENSE:CORRECTION:LEVEL:SHIFT "+str(Level_Offset)+"DB")  #Establece un offset en el calculo de la potencia
    OSA.write(":DISPLAY:TRACE:Y1:RLEVEL "+str(Level_Ref)+"DBM")         #Establece un offset en la visualizacion
    OSA.write(":INIT:SMODE "+Sweep_Mode)                                #Establece el modo de barrido
    OSA.write(":SENSE:SWEEPp:SPEED "+Sweep_Speed)                       #Establece la velocidad de barrido
    OSA.write(":SENSE:SETTING:FCONNECTOR "+fiber_conector)                 #Establece el tipo de fibra

    return OSA

def Config_OPM_Thorlabs(Instrumento,Muestras_Prom):
    OPM = rm.open_resource(Instrumento)                         #Inicializa el recurso del OPM
    OPM.write("SENS:AVER:COUNT "+str(Muestras_Prom))            #Muestras para el promedio
    print (OPM.query('*IDN?'))                                  #Mensaje de Identificacion del protocolo

    return OPM

def VCSEL_Current_Sweep(Recurso_VCSEL_T,Min_Voltaje,Max_Voltaje,Step_Voltaje,Recurso_OSA,Recurso_OPM,Base_Current):
    Voltaje_Ideal = []                            #Corrientes del barrido
    OSA_Wavelength = []                     #Longitudes de onda del barrido
    OPM_power = []                          #Potencia del barrido
    Time = []                               #Tiempo de ejecucion del barrido

    time_ref=time.time()                    #Obtiene el tiempo inicial como referencia
    time_meas=0                             #Variable comodin para obtener el tiempo

    Osameas_wavelength=0                    #Variable comodin para obtener el valor numerico de la longitud de onda
    Osaread_wavelength=0                    #Variable que lee la longitud de onda

    OPMmeas_power=0                         #Variable comodin para obtener el valor numerico de la potencia        
    OPMread_power=0                         #Variable que lee la potencia


    Recurso_VCSEL_T.write("SETDC:"+str(int(Min_Voltaje)))   #Establece la tension #000 a #999  -> 0v a -20v
    Recurso_VCSEL_T.write("SETC:"+str(round(float(Base_Current),1))) #Establece la corriente en #xx.xmA 

    for i in np.arange(Min_Voltaje,Max_Voltaje,Step_Voltaje):   #Barrido de corriente
        Recurso_VCSEL_T.write("SETDC:"+str(int(i)))   #Establece la tension #000 a #999  -> 0v a -20v
        

        Recurso_OSA.write(":CALCULATE:MARKER:AUTO ON")              #Busca la posicion del pico de potencia automaticamente luego de un barrido
        Recurso_OSA.write("*CLS")                                   #Limpia el registro del OSA
        Recurso_OSA.write(":INIT")                                  #Inicia el barrido del OSA
        
        query_done = False                                          #Variable para esperar los datos del OSA
        Recurso_OSA.write("CALCULATE:MARKER:X? 0")                  #Pregunta el valor de longitud de onda del marcador (Pico de potencia)
        while not query_done:
            try:
                Osaread_wavelength = Recurso_OSA.query("")          #Obtiene el valor de longitud de onda del marcador (Pico de potencia)
                query_done = True
            except:
                pass
        Osameas_wavelength=float(Osaread_wavelength)                #Obtiene el valor numerico de la longitud de onda pico
        
        Recurso_OPM.write("*CLS")                                   #Limpia el registro del OPM
        OPMread_power=Recurso_OPM.query("READ?")                    #Lee la potencia optica del OPM
        OPMmeas_power=float(OPMread_power)                          #Obtiene el valor numerico de la potencia optica

        time_meas = time.time() - time_ref                          #Obtiene el tiempo de ejecucion del n paso de corriente

        OSA_Wavelength.append(Osameas_wavelength)                   #Acumula la lista de longitud de onda
        OPM_power.append(OPMmeas_power)                             #Acumula la lista de potencia
        Time.append(time_meas)                                      #Acumula la lista de tiempo
        Voltaje_Ideal.append(i)                                     #Acumula la lista de corriente ideal

    Recurso_VCSEL_T.write("SETC:"+str(round(float(0),1))) #Establece la corriente en #xx.xmA 

    return Time,Voltaje_Ideal,OSA_Wavelength,OPM_power


rm = pyvisa.ResourceManager()

###### Configuracion de la fuente de corriente de Thorlabs
VCSEL_T=Config_VCSEL_T(visa_OSA,temp_set,Voltage_min,Vcsel_mode)

###### Configuracion del analizador de espectros optico
OSA=Config_OSA_Yokogawa(visa_OSA,OSA_display,wavelength_center,wavelength_span,osa_resolution,osa_sensitivity,level_offset,level_ref,sweep_mode,sweep_speed)

###### Configuracion del medidor de potencia optica
OPM=Config_OPM_Thorlabs(visa_OPM,muestras_prom)

###### Mediciones 
for i in range(1,Repeticiones+1):
    
    Tiempo,Corriente,Voltaje_Barrido,Longitud_Onda,Potencia=VCSEL_Current_Sweep(VCSEL_T,Voltage_min,Voltage_max,Voltage_step,OSA,OPM,current)

    ####################### Data to .csv ##########################
    filename = "VCSEL_1550_T_Caracterizacion_"+dt_string+"_Temp_"+str(temp_set)+"_Voltaje_Step_"+str(Voltage_step)+"_OPM_OSA"+str(i)+".csv"
    file = open(filename,"w")
    file.write("Time,Voltaje_Ideal,Wavelength,Power\n")
    for s in range(len(Tiempo)-1):
        file.write(str(Tiempo[s])+","+str(Voltaje_Barrido[s])+","+str(Longitud_Onda[s])+","+str(Potencia[s])+"\n")
    file.close()
    
    plt.plot(Corriente, Longitud_Onda)
    plt.show()

    plt.plot(Corriente, Potencia)
    plt.show()

     
###### End ######
OSA.close()
OPM.close()
VCSEL_T.close()


####################### Plotting ##########################

plt.plot(Voltaje_Barrido, Longitud_Onda)
plt.show()

plt.plot(Voltaje_Barrido, Potencia)
plt.show()





