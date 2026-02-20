import threading
import queue
import time
import random

# Configuración
NUM_EMPLEADOS = 3
DOCUMENTOS_POR_EMPLEADO = 5

# Cola FIFO de impresión
cola_impresion = queue.Queue()


class Empleado(threading.Thread):
    def __init__(self, id_empleado, cola):
        super().__init__()
        self.id_empleado = id_empleado
        self.cola = cola

    def run(self):
        for i in range(1, DOCUMENTOS_POR_EMPLEADO + 1):
            time.sleep(random.uniform(0.5, 2))  # Simula tiempo de creación
            documento = f"Doc-{i} (Empleado {self.id_empleado})"
            
            self.cola.put(documento)
            print(f"[Empleado {self.id_empleado}] Envió {documento}")

        print(f"[Empleado {self.id_empleado}] Terminó de enviar documentos.")


class Impresora(threading.Thread):
    def __init__(self, cola):
        super().__init__()
        self.cola = cola

    def run(self):
        while True:
            documento = self.cola.get()

            # Señal para terminar
            if documento is None:
                self.cola.task_done()
                break

            print(f"    [Impresora] Imprimiendo {documento}...")
            time.sleep(random.uniform(1, 3))  # Tiempo de impresión
            print(f"    [Impresora] Terminado {documento}")

            self.cola.task_done()

        print("    [Impresora] No hay más documentos. Apagando...")


def main():
    # Crear impresora (consumidor)
    impresora = Impresora(cola_impresion)
    impresora.start()

    # Crear empleados (productores)
    empleados = []
    for i in range(1, NUM_EMPLEADOS + 1):
        empleado = Empleado(i, cola_impresion)
        empleado.start()
        empleados.append(empleado)

    # Esperar a que los empleados terminen
    for empleado in empleados:
        empleado.join()

    # Esperar a que se impriman todos los documentos
    cola_impresion.join()

    # Enviar señal de parada a la impresora
    cola_impresion.put(None)
    impresora.join()

    print("\nSistema de impresión finalizado correctamente.")


if __name__ == "__main__":
    main()