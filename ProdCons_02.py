"""
PRODUCTOR CONSUMIDOR 02

Tenemos 3 productores que pueden generar hasta 2 elementos, 1 consumidor y un almacen de tamaño NPROD

Cada productor genera un numero aleatorio y ponen en wait los semaforos empty. 
Almacenan los numeros y mandan un signal al los semaforos non_empty. 
Cuando el productor ya haya generado todos los numeros posibles pone un -1 en el almacen

El consumidor manda un wait a los non_empty, crea una lista running donde habrá:
    TRUE si los productores pueden  seguir generando numeros
    FALSE si el productor no puede generar más
Después consume el minimo numero almacenado, guarda la posición para avisar al productor correspondiente y manda un signal.

El proceso para cuando todos los productores hayan generado 2 elementos.

"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random


N = 2  #Cantidad de numeros que se pueden producir
NPROD = 3 #Num de productores
NCONS = 1 #Num de consumidores


def productor(pid, almacen, empty, non_empty):
    dato = random.randint(1,5)
    
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(1,5)
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()   #Avisamos a los non_empty de que añadimos un numero
    
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    almacen[pid] = -1
    non_empty[pid].release()


def consumidor(almacen, empty, non_empty):
    for s in non_empty:
        s.acquire()
        print (f"consumidor {current_process().name} desalmacenando")
    
    running = [True for _ in range (NPROD)]
    ordenada = [] #Lista ordenada de los numeros consumidos
    
    while True in running:
        numeros = [] #Lista con los numeros generados para buscar el minimo
        for i in range(NPROD):
            running[i] = almacen[i]>=0
            if running[i]:
                numeros.append(almacen[i])
        if numeros == []:
            break
        
        dato = min(numeros)
        ordenada.append(dato)
        posicion = almacen[:].index(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire()   
                
def main():
    #listas de semaforos
    empty = [BoundedSemaphore(1) for i in range (NPROD)] 
    non_empty = [Semaphore(0) for i in range (NPROD)]
    
    almacen = Array('i', NPROD) #almacen vacio
    
    prodlst = [ Process(target = productor,
                        name = f'prod_{i}',
                        args = (i, almacen, empty, non_empty))
                for i in range(NPROD) ]

    cons = [ Process(target = consumidor,
                     name = f"cons_",
                     args = (almacen, empty, non_empty))]
    
    for p in prodlst + cons:
        p.start()

    for p in prodlst + cons:
        p.join()   
    
if __name__ == '__main__':
    main()