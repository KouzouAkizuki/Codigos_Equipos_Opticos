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
#   voltaje: [V]

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

############################# Multimeter parameters #########################

visa_Multimeter='ASRL5::INSTR'      #Nombre del recurso VISA
mode='VDC'              #Modo de medicion de tension DC

############################# OPM parameters #########################

visa_OPM='USB0::0x1313::0x8078::P0023445::INSTR'    #Nombre del recurso VISA

muestras_prom=1

############################# Parametros del Experimento #########################

Repeticiones=40

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

def Config_Multimeter_Fluke(Instrumento,Modo):
    Multimeter=rm.open_resource(Instrumento)                 #Inicializa el recurso del multimetro
    Multimeter.baud_rate = 19200                               
    Multimeter.break_lenght = 256                              
    Multimeter.timeout = 1500
    
    query_done = False                                          #Variable para esperar los datos del OSA
    while not query_done:
        try:
            Multimeter.read()          #Obtiene el valor de longitud de onda del marcador (Pico de potencia)
        except:
            query_done = True

    
    print (Multimeter.query('*IDN?'))                          #Mensaje de Identificacion del protocolo

    Multimeter.write(Modo)
    Multimeter.write('TRIGGER 1')
    Multimeter.write('AUTO')
    
                    
    query_done = False                                          #Variable para esperar los datos del OSA
    while not query_done:
        try:
            Multimeter.read()          #Obtiene el valor de longitud de onda del marcador (Pico de potencia)
        except:
            query_done = True


    return Multimeter

def Config_OPM_Thorlabs(Instrumento,Muestras_Prom):
    OPM = rm.open_resource(Instrumento)                         #Inicializa el recurso del OPM
    OPM.write("SENS:AVER:COUNT "+str(Muestras_Prom))            #Muestras para el promedio
    print (OPM.query('*IDN?'))                                  #Mensaje de Identificacion del protocolo

    return OPM

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

def VCSEL_Current_Sweep(Recurso_Isource,Min_Current,Max_Current,Step_Current,Recurso_Multimetro,Recurso_OPM):
    Current = []                            #Corrientes del barrido
    Current_Ideal=[]                        #Corriente ideal
    Voltaje = []                     #Longitudes de onda del barrido
    Time = []                               #Tiempo de ejecucion del barrido
    OPM_power = []                          #Potencia del barrido

    time_ref=time.time()                    #Obtiene el tiempo inicial como referencia
    time_meas=0                             #Variable comodin para obtener el tiempo

    Imeas=0                                 #Variable comodin para obtener el valor numerico de la corriente
    Iread=0                                 #Variable que lee la corriente

    Multimetermeas_voltaje=0                         #Variable comodin para obtener el valor numerico de la tension    
    Multimeterread_voltaje=0                         #Variable que lee la tension

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

        Multimeterread_voltaje=Recurso_Multimetro.query("VAL1?")           #Lee la tension del Multimetro
        Recurso_Multimetro.read()
        Multimeterread_voltaje=Multimeterread_voltaje.split(" ")
        Multimetermeas_voltaje=float(Multimeterread_voltaje[0])               #Obtiene el valor numerico de la tension del multimetro

        Recurso_OPM.write("*CLS")                                   #Limpia el registro del OPM
        OPMread_power=Recurso_OPM.query("READ?")                    #Lee la potencia optica del OPM
        OPMmeas_power=float(OPMread_power)                          #Obtiene el valor numerico de la potencia optica


        time_meas = time.time() - time_ref                          #Obtiene el tiempo de ejecucion del n paso de corriente

        OPM_power.append(OPMmeas_power)                             #Acumula la lista de potencia
        Voltaje.append(Multimetermeas_voltaje)                      #Acumula la lista de tension
        Time.append(time_meas)                                      #Acumula la lista de tiempo
        Current.append(Imeas)                                       #Acumula la lista de corriente
        Current_Ideal.append(i)                                     #Acumula la lista de corriente ideal

    Recurso_Isource.write(":LASER OFF")                             #Apaga el Laser
    Recurso_Isource.write(':TEC OFF')                               #Apaga el TEC

    return Time,Current,Current_Ideal,Voltaje,OPM_power


rm = pyvisa.ResourceManager()

###### Configuracion de la fuente de corriente de Thorlabs
Isource=Config_VCSEL_Thorlabs(visa_Isource,slot,source_operation_mode,tec_current_limit_sw,current_limit_SW,ldpol,pdpol,Pshare,Dshare,Ishare,Ishare_Status)

###### Configuracion del multimetro FLUKE
Multimeter=Config_Multimeter_Fluke(visa_Multimeter,mode)

###### Configuracion del medidor de potencia optica
OPM=Config_OPM_Thorlabs(visa_OPM,muestras_prom)


###### Inicia el TEC en una temperatura Inicial
Basic_Temp_Set(Isource,temp_start,temp_tol)
Basic_Temp_Set(Isource,temp_start,temp_tol)             #Doble verificacion por si existen sobrepicos

###### Mediciones 
for i in range(1,Repeticiones+1):
    Basic_Temp_Set(Isource,temp_start,temp_tol)             
    Basic_Temp_Set(Isource,temp_start,temp_tol)             #Doble verificacion por si existen sobrepicos
    Tiempo,Corriente,Corriente_Barrido,Voltaje,Potencia=VCSEL_Current_Sweep(Isource,current_min,current_max,current_step,Multimeter,OPM)

    ####################### Data to .csv ##########################
    filename = "Fotodiodo_FGA01FC_SSFBG_"+dt_string+"_Temp_VCSEL_"+str(temp_start)+"_Current_Step_"+str(current_step)+"_Multimeter_"+str(i)+".csv"
    file = open(filename,"w")
    file.write("Time,Current,Current_Ideal,Voltaje,Power\n")
    for s in range(len(Tiempo)-1):
        file.write(str(Tiempo[s])+","+str(Corriente[s])+","+str(Corriente_Barrido[s])+","+str(Voltaje[s])+","+str(Potencia[s])+"\n")
    file.close()
    
    plt.plot(Corriente, Voltaje)
    plt.show()

    plt.plot(Corriente, Potencia)
    plt.show()

        
###### End ######
Multimeter.close()
Isource.close()
OPM.close()






