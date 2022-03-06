# -*- coding: utf-8 -*-
"""
PRODUCTOR CONSUMIDOR 01

Tenemos 3 productores, 1 consumidor y un almacen de tamaño NPROD

Cada productor genera un numero aleatorio y ponen en wait los semaforos empty. 
Almacenan los numeros y mandan un signal al los semaforos non_empty

El consumidor manda un wait a los non_empty y consume el minimo numero almacenado.
Después envía un signal al semaforo empty del productor cuyo elemento ha consumido para que genere uno nuevo.

El productor debe generar los numeros de manera creciente y asi contunúa actuando el proceso de manera infinita.

"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random

import numpy as np

NPROD = 3 #Num de productores
NCONS = 1 #Num de consumidores


def productor(pid, almacen, empty, non_empty):
    dato = random.randint(0,5)
    while True:
        empty[pid].acquire()
        dato += random.randint(0,5)
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()
        
def consumidor(almacen, empty, non_empty):
    for s in non_empty:
      s.acquire()
      print (f"consumidor {current_process().name} desalmacenando")
    ordenada = []
    while True:
        dato = np.amin(almacen)
        ordenada.append(dato)
        posicion = almacen[:].index(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire()
    print(ordenada)
  
def main():
    #listas de semaforos
    empty = [BoundedSemaphore(1) for i in range (NPROD)] 
    non_empty = [Semaphore(0) for i in range (NPROD)]
    
    almacen = Array('i', NPROD) #almacen vacio
    
    print("almacen inicial", almacen[:])
    
    prodlst = [Process(target = productor,
                        name = f'prod_{i}',
                        args = (i, almacen, empty, non_empty))
                for i in range(NPROD)]
    cons = [Process(target = consumidor,
                     name = f"cons_",
                     args = (almacen, empty, non_empty))]
    
    for p in prodlst + cons:
        p.start()
        
    for p in prodlst + cons:
        p.join()
           
if __name__ == '__main__':
    main()