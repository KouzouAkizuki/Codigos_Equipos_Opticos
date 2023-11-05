# -*- coding: utf-8 -*-
"""
Created on Thu Sep  28 10:23:00 2023

@author: Oscar_Riveros & CMUN 
"""

import pyvisa
from pyvisa import constants

from enum import Enum

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

############################# Thorlabs ITC8000 Source Parameters #########################

visa_Isource='ASRL3::INSTR'    #Nombre del recurso VISA

slot = 1                        #Ranura del Laser
temp_start = 20                 #Temperatura inicial del Laser
temp_tol = 0.1                  #Tolerancia de temperatura del Laser
tec_current_limit_sw=0.7        #Limite de corriente del TEC del Laser

current_limit_SW = 0.012        #Limite de corriente del laser
source_operation_mode = "CC"    #CC: constant current; CP: constant Power
ldpol="CG"                      #Polarizacion del Laser
pdpol="AG"                      #Polarizacion del fotodiodo del Laser

Pshare=40                       #Constante proporcional del PID de temperatura
Dshare=8                        #Constante derivativa del PID de temperatura
Ishare=30                       #Constante integrativa del PID de temperatura
Ishare_Status='ON'              #Activacion de la constante integrativa

###########################################################################################

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
        txt = Recurso_Isource.query(":TEMP:ACT?")                      #Pregunta la temperatura
        temp_ac = txt.split(" ")
        temp_ac = float(temp_ac[1])                                 
        print("temp: "+ str(temp_ac))

def Temp_Step(Recurso_Isource,Temperatura,Tiempo):     
    Time = []                                                       #Lista del tiempo
    Temperature = []                                                #Lista de temperaturas


    Recurso_Isource.write("*CLS")                                  #Limpia la memoria de la fuente Thorlabs
    Recurso_Isource.write(":TEMP:SET "+str(float(Temperatura)))    #Coloca una temperatura en la fuente
    time_temp_ref=time.time()                                       #Obtiene el tiempo inicial como referencia

    Recurso_Isource.write(':TEC ON')                               #Prende el TEC de la fuente

    txt = Recurso_Isource.query(":TEMP:ACT?")                      #Pregunta la temperatura a la fuente
    temp_ac = txt.split(" ")
    temp_ac = float(temp_ac[1])
    time_temp=time.time()-time_temp_ref                             #Obtiene el tiempo que ha pasado

    Time.append(time_temp)                                          #Acumula la lista de tiempo
    Temperature.append(temp_ac)                                     #Acumula la lista de temperaturas

    while (time_temp<Tiempo):                                       #Ejecuta el codigo hasta que pase la cantidad de segundos de la variable Tiempo
        txt = Recurso_Isource.query(":TEMP:ACT?")                      #Pregunta la temperatura
        temp_ac = txt.split(" ")
        temp_ac = float(temp_ac[1])
        time_temp=time.time()-time_temp_ref                             #Obtiene el tiempo

        Time.append(time_temp)                                          #Acumula la lista de tiempo
        Temperature.append(temp_ac)                                     #Acumula la lista de temperaturas
        
        print("time: "+str(time_temp)+", temp: "+ str(temp_ac))

    return Time,Temperature


rm = pyvisa.ResourceManager()           #Administrador de recursos de PyVISA


###### Configuracion de la fuente de corriente de Thorlabs
Isource=Config_VCSEL_Thorlabs(visa_Isource,slot,source_operation_mode,tec_current_limit_sw,current_limit_SW,ldpol,pdpol,Pshare,Dshare,Ishare,Ishare_Status)

###### Inicia el TEC en una temperatura Inicial
Basic_Temp_Set(Isource,temp_start,temp_tol)
Basic_Temp_Set(Isource,temp_start,temp_tol)             #Doble verificacion por si existen sobrepicos

###### Barrido de temperatura
Segundos=60                      #Cantidad de tiempo del barrido
Temperatura_end=30              #Temperatura final del paso
tiempo_barrido_1,temperatura_barrido_1=Temp_Step(Isource,Temperatura_end,Segundos)
tiempo_barrido_2,temperatura_barrido_2=Temp_Step(Isource,temp_start,Segundos)

###### End ######
Isource.write(":LASER OFF")    #Apaga el Laser
Isource.write(':TEC OFF')      #Apaga el TEC
Isource.close()                #Cierra el recurso de la fuente de thorlabs


####################### Data to .csv ##########################
filename = "VCSEL_1550_SM_PID_"+dt_string+"_Pshare_"+str(Pshare)+"_Dshare_"+str(Dshare)+"_Ishare_"+str(Ishare)+"_Ishare_Status_"+Ishare_Status+"_Tiempo_"+str(Segundos)+".csv"  
file = open(filename,"w")
file.write("time_1,Temp_1,time_2,Temp_2\n")
for s in range(len(tiempo_barrido_1)-1):
    file.write(str(tiempo_barrido_1[s])+","+str(temperatura_barrido_1[s])+","+str(tiempo_barrido_2[s])+","+str(temperatura_barrido_2[s])+"\n")
file.close()


####################### Plotting ##########################

plt.plot(tiempo_barrido_1, temperatura_barrido_1)
plt.show()

plt.plot(tiempo_barrido_2, temperatura_barrido_2)
plt.show()





