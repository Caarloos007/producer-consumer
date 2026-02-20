import threading
import queue
import time
import random
import json
from datetime import datetime

# Configuración
NUM_EMPLEADOS = 3
DOCUMENTOS_POR_EMPLEADO = 5

# Cola FIFO de impresión
cola_impresion = queue.Queue()

# Registro de actividades
registro = []
lock = threading.Lock()  # Para acceso seguro al registro


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
            
            # Registrar envío
            with lock:
                registro.append({
                    "evento": "enviado",
                    "documento": documento,
                    "empleado": self.id_empleado,
                    "timestamp": datetime.now().isoformat()
                })
            
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
            
            # Registrar impresión
            with lock:
                registro.append({
                    "evento": "impreso",
                    "documento": documento,
                    "timestamp": datetime.now().isoformat()
                })


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

    
    # Guardar registro en JSON
    with open("reporte_impresion.json", "w", encoding="utf-8") as f:
        json.dump({
            "sistema": "Cola FIFO",
            "configuracion": {
                "num_empleados": NUM_EMPLEADOS,
                "documentos_por_empleado": DOCUMENTOS_POR_EMPLEADO
            },
            "registro": registro
        }, f, indent=2, ensure_ascii=False)
    
    print("✓ Reporte guardado en 'reporte_impresion.json'")
    # Esperar a que se impriman todos los documentos
    cola_impresion.join()

    # Enviar señal de parada a la impresora
    cola_impresion.put(None)
    impresora.join()

    print("\nSistema de impresión finalizado correctamente.")


if __name__ == "__main__":
    main()