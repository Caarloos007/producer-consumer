import threading
import queue
import time
import random
import json
from datetime import datetime

# Configuración
NUM_EMPLEADOS = 3
DOCUMENTOS_POR_EMPLEADO = 5
NUM_IMPRESORAS = 2

# Cola con prioridad (menor número = mayor prioridad)
cola_impresion = queue.PriorityQueue()

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
            time.sleep(random.uniform(0.5, 2))

            prioridad = random.randint(1, 3)  # 1 = urgente, 3 = normal
            documento = f"Doc-{i} (Empleado {self.id_empleado})"

            # Se añade tupla (prioridad, contador, documento)
            # contador evita conflictos si prioridades son iguales
            self.cola.put((prioridad, time.time(), documento))

            # Registrar envío
            with lock:
                registro.append({
                    "evento": "enviado",
                    "documento": documento,
                    "empleado": self.id_empleado,
                    "prioridad": prioridad,
                    "timestamp": datetime.now().isoformat()
                })

            print(f"[Empleado {self.id_empleado}] Envió {documento} con prioridad {prioridad}")

        print(f"[Empleado {self.id_empleado}] Terminó.")


class Impresora(threading.Thread):
    def __init__(self, id_impresora, cola):
        super().__init__()
        self.id_impresora = id_impresora
        self.cola = cola
        self.activa = True

    def simular_fallo(self):
        # 20% probabilidad de fallo
        if random.random() < 0.2:
            print(f"    ⚠️ [Impresora {self.id_impresora}] FALLO (sin papel / mantenimiento)")
            tiempo_reparacion = random.randint(3, 6)
            time.sleep(tiempo_reparacion)
            print(f"    ✅ [Impresora {self.id_impresora}] Reparada y operativa")

    def run(self):
        while True:
            prioridad, timestamp, documento = self.cola.get()

            # Registrar impresión
            with lock:
                registro.append({
                    "evento": "impreso",
                    "documento": documento,
                    "impresora": self.id_impresora,
                    "prioridad": prioridad,
                    "timestamp": datetime.now().isoformat()
                })

            if documento is None:
                self.cola.task_done()
                break

            self.simular_fallo()

            print(f"    [Impresora {self.id_impresora}] Imprimiendo {documento} (Prioridad {prioridad})")
            time.sleep(random.uniform(1, 3))
            print(f"    [Impresora {self.id_impresora}] Terminado {documento}")

            self.cola.task_done()

        print(f"    [Impresora {self.id_impresora}] Apagando...")


def main():
    impresoras = []
    for i in range(1, NUM_IMPRESORAS + 1):
        imp = Impresora(i, cola_impresion)
        imp.start()
        impresoras.append(imp)

    empleados = []
    for i in range(1, NUM_EMPLEADOS + 1):
        emp = Empleado(i, cola_impresion)
        emp.start()
        empleados.append(emp)

    # Esperar empleados
    for emp in empleados:
        emp.join()

    # Esperar que se impriman todos
    
    # Guardar registro en JSON
    with open("reporte_impresion_prioridad.json", "w", encoding="utf-8") as f:
        json.dump({
            "sistema": "Cola con Prioridad",
            "configuracion": {
                "num_empleados": NUM_EMPLEADOS,
                "documentos_por_empleado": DOCUMENTOS_POR_EMPLEADO,
                "num_impresoras": NUM_IMPRESORAS
            },
            "registro": registro
        }, f, indent=2, ensure_ascii=False)
    
    print("✓ Reporte guardado en 'reporte_impresion_prioridad.json'")
    cola_impresion.join()

    # Señal de parada para cada impresora
    for _ in impresoras:
        cola_impresion.put((999, time.time(), None))

    for imp in impresoras:
        imp.join()

    print("\nSistema de impresión finalizado correctamente.")


if __name__ == "__main__":
    main()