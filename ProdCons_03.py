"""
PRODUCTOR CONSUMIDOR 03

Tenemos 3 productores que pueden generar hasta 2 elementos, 1 consumidor y un almacen de tamaño infinito.

Cada productor genera un numero aleatorio y ponen en wait los semaforos empty. 
Almacenan los numeros de manera que quede un numero de 4 digitos con el pid del productor y el numero generado.
Mandan un signal al los semaforos non_empty. 
Cuando el productor ya haya generado todos los numeros posibles mantiene el signal en el non_empty

El consumidor manda un wait a los non_empty, y crea listas auxiliares para buscar el minimo, su posición y el productor que no generó.
Busca el minimo de los numeros generados posibles y guarda el numero y la posicion. 
Lo consume y pone en su lugar un -2.
Manda un signal al empty  y un wait al non_empty del productor que tiene que generar de nuevo.


El proceso para cuando todos los productores hayan generado 2 elementos.

"""
from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

N = 3 # Cantidad de productos que puede fabricar cada productor 
K = 2 #Numero de casillas que le corresponden a cada productor
NPROD = 3 #Numero de productores

def add_data(almacen, pid, data, mutex):
    mutex.acquire()
    try:
        almacen.append(pid*1000 + data)
        sleep(1)
    finally:
        mutex.release()


def productor(almacen, pid, empty, non_empty, mutex, acabado):
    dato = random.randint(0,5)
    
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(0,5)
        print (f"productor {current_process().name} produciendo")
        add_data(almacen, pid, dato, mutex)
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()   #Avisamos a los non_empty de que añadimos un numero
    
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    sleep(1)
    non_empty[pid].release()
    
    
def consumidor(almacen, empty, non_empty, mutex):
    for s in non_empty:
        s.acquire()
    print (f"consumidor {current_process().name} desalmacenando")
    sleep(1)
    
    ordenados = [] #Lista ordenada de los numeros consumidos
    while len(ordenados) < NPROD * N:
        numeros = [] #Lista con los numeros donde buscar el minimo
        lista_posicion = [] #Lista con las posiciones de los numeros
        for i in range(len(almacen)):
            if almacen[i] >= 0:
                numeros.append(almacen[i] % 1000)
                lista_posicion.append(almacen[i]//1000)
        
        if numeros == []: #Si 'numeros' se queda vacia hemos acabado
            break
        
        dato = min(numeros)
        posicion = lista_posicion[numeros.index(dato)]
        posicion_almacen = almacen[:].index(dato + posicion * 1000) 
        
        almacen[posicion_almacen]= -2 
        ordenados.append(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire() 

def main():
    manager = Manager()
    almacen = manager.list()
    acabado = Array('i', NPROD)
    
    non_empty = [Semaphore(0) for i in range (NPROD)] #Lista de semaforos
    empty = [BoundedSemaphore(K) for _ in range (NPROD)]
    mutex = Lock()
    
    
    prodlst = [Process(target=productor,
                        name=f'prod_{i}',
                        args=(almacen, i, empty, non_empty, mutex, acabado))
                for i in range(NPROD)]
    cons = [ Process(target=consumidor,
                      name=f"cons_",
                      args=(almacen, empty, non_empty, mutex))]
    
    for p in prodlst + cons:
        p.start()
    
    for p in prodlst + cons:
        p.join()

if __name__ == '__main__':
    main()