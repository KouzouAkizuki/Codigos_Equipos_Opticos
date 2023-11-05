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
#   current: [A]
#   temperature: [°C]
#   Longitud de onda: [m]
#   Potencia OPM: [W]

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

######################################################################

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

def VCSEL_Current_Sweep(Recurso_Isource,Min_Current,Max_Current,Step_Current,Recurso_OSA,Recurso_OPM):
    Current = []                            #Corrientes del barrido
    Current_Ideal=[]                        #Corriente ideal
    OSA_Wavelength = []                     #Longitudes de onda del barrido
    OPM_power = []                          #Potencia del barrido
    Time = []                               #Tiempo de ejecucion del barrido

    time_ref=time.time()                    #Obtiene el tiempo inicial como referencia
    time_meas=0                             #Variable comodin para obtener el tiempo

    Imeas=0                                 #Variable comodin para obtener el valor numerico de la corriente
    Iread=0                                 #Variable que lee la corriente

    Osameas_wavelength=0                    #Variable comodin para obtener el valor numerico de la longitud de onda
    Osaread_wavelength=0                    #Variable que lee la longitud de onda

    OPMmeas_power=0                         #Variable comodin para obtener el valor numerico de la potencia        
    OPMread_power=0                         #Variable que lee la potencia


    Recurso_Isource.write(":ILD:SET "+str(float(Min_Current)))  #Coloca una corriente en el Laser
    Recurso_Isource.write(":LASER ON")                          #Enciende el Laser

    for i in np.arange(Min_Current,Max_Current,Step_Current):   #Barrido de corriente
        Recurso_Isource.write(":ILD:SET "+str(float(i)))            #Establede una corriente para el Laser
        
        Iread=Recurso_Isource.query(":ILD:ACT?")                    #Pregunta la corriente de la fuente de corriente
        print(Iread)
        Imeas=Iread.split(" ")
        Imeas=float(Imeas[1])

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
        Current.append(Imeas)                                       #Acumula la lista de corriente
        Current_Ideal.append(i)                                     #Acumula la lista de corriente ideal

    Recurso_Isource.write(":LASER OFF")                             #Apaga el Laser
    Recurso_Isource.write(':TEC OFF')                               #Apaga el TEC

    return Time,Current,Current_Ideal,OSA_Wavelength,OPM_power


rm = pyvisa.ResourceManager()

###### Configuracion de la fuente de corriente de Thorlabs
Isource=Config_VCSEL_Thorlabs(visa_Isource,slot,source_operation_mode,tec_current_limit_sw,current_limit_SW,ldpol,pdpol,Pshare,Dshare,Ishare,Ishare_Status)

###### Configuracion del analizador de espectros optico
OSA=Config_OSA_Yokogawa(visa_OSA,OSA_display,wavelength_center,wavelength_span,osa_resolution,osa_sensitivity,level_offset,level_ref,sweep_mode,sweep_speed)

###### Configuracion del medidor de potencia optica
OPM=Config_OPM_Thorlabs(visa_OPM,muestras_prom)

###### Inicia el TEC en una temperatura Inicial
Basic_Temp_Set(Isource,temp_start,temp_tol)
Basic_Temp_Set(Isource,temp_start,temp_tol)             #Doble verificacion por si existen sobrepicos

###### Mediciones 
Tiempo,Corriente,Corriente_Barrido,Longitud_Onda,Potencia=VCSEL_Current_Sweep(Isource,current_min,current_max,current_step,OSA,OPM)
     
###### End ######
OSA.close()
OPM.close()
Isource.close()

####################### Data to .csv ##########################
filename = "VCSEL_1550_SM_Caracterizacion_"+dt_string+"_Temp_"+str(temp_start)+"_Current_Step_"+str(current_step)+"_OPM_OSA_.csv"
file = open(filename,"w")
file.write("Time,Current,Current_Ideal,Wavelength,Power\n")
for s in range(len(Tiempo)-1):
    file.write(str(Tiempo[s])+","+str(Corriente[s])+","+str(Corriente_Barrido[s])+","+str(Longitud_Onda[s])+","+str(Potencia[s])+"\n")
file.close()

####################### Plotting ##########################

plt.plot(Corriente, Longitud_Onda)
plt.show()

plt.plot(Corriente, Potencia)
plt.show()





