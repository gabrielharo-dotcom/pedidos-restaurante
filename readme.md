# Sistema básico de pedidos de restaurante

**Trabajo final de Estructuras de Datos · Batería 2 · Ejercicio 1**

## Integrantes

- Gabriel Haro Vargas
- Jeremy Wensceslao Cervantes Rosales

## Introducción

Un restaurante pequeño que registra sus pedidos en papel puede perder el orden de llegada o pasar por alto un pedido urgente. Este programa de consola organiza los pedidos con dos prioridades. Los **urgentes** tienen prioridad **1** y los **normales**, prioridad **2**. Dentro de cada prioridad se respeta FIFO (*First In, First Out*), es decir, se atiende primero el pedido que llegó primero.

Cada pedido guarda un número único dentro de la sesión, el nombre del cliente, el tipo, la prioridad, la fecha y hora local de registro, y su estado. El sistema asigna números consecutivos desde 1. Los datos se mantienen en memoria durante la ejecución.

## Cómo ejecutar el programa

Desde la carpeta del proyecto, con Python 3:

~~~bash
python pedidos_restaurante.py
~~~

Para ejecutar las pruebas incorporadas:

~~~bash
python pedidos_restaurante.py --pruebas
~~~

Las pruebas cubren el orden por prioridad y FIFO, la cancelación y reutilización de las colas, los cambios de estado, la espera estimada y la validación del registro.

## Estructura de datos y diseño de clases

La cola de prioridad se implementó desde cero con **dos colas FIFO enlazadas**, una para urgentes y otra para normales. Cada cola guarda referencias al frente y al final, además de un contador. Así se puede insertar al final y retirar del frente en tiempo constante. El desempate usa el orden de inserción, que se conserva incluso si dos pedidos tienen la misma hora de registro.

| Clase | Responsabilidad |
| --- | --- |
| [Pedido](pedidos_restaurante.py) | Guarda los datos del pedido y representa su estado. |
| Nodo | Guarda un pedido y una referencia al siguiente nodo. |
| ColaFIFO | Encola, desencola y permite retirar un pedido por número. |
| ColaPrioridad | Selecciona la cola correspondiente y da preferencia a los urgentes. |
| SistemaPedidos | Gestiona los pendientes, los pedidos en preparación y el último pedido atendido. |

La selección del siguiente pedido en la clase ColaPrioridad es:

~~~python
def desencolar(self):
    # Usar el frente de urgentes siempre que exista.
    if self.urgentes.cantidad:
        return self.urgentes.desencolar()
    return self.normales.desencolar()
~~~

Al cancelar un pendiente o completar un pedido en preparación, se busca su número en la cola correspondiente. Una vez localizado, se reconectan los nodos vecinos y se actualizan los extremos si corresponde. El resto de los pedidos conserva su orden.

## Operaciones y complejidad

Sea **n** la cantidad de pedidos pendientes y **p** la cantidad de pedidos en preparación. Los tiempos corresponden al peor caso y al manejo de la estructura de datos.

| Opción | Operación | Comportamiento | Tiempo |
| --- | --- | --- | --- |
| 1 | Registrar | Asigna número, prioridad y hora. Encola al final del tipo correspondiente. | O(1) |
| 2 | Atender siguiente | Extrae el primer urgente disponible o el primer normal si la cola urgente está vacía. Pasa el pedido a preparación. | O(1) |
| 3 | Completar | Muestra los pedidos en preparación y retira el que coincide con el número ingresado. | O(p) |
| 4 | Cancelar | Busca por número y retira el pedido si todavía está pendiente. | O(n) |
| 5 | Listar pendientes | Recorre primero urgentes y luego normales en orden de llegada. | O(n) |
| 6 | Contar por tipo | Lee el contador de cada cola de pendientes. | O(1) |
| 7 | Ver último atendido | Muestra el último pedido que pasó a preparación, con su estado actual. | O(1) |
| 8 | Calcular espera | Recorre los pendientes en orden y acumula sus tiempos estimados. | O(n) |
| 0 | Salir | Termina la sesión de consola. | O(1) |

Cada pedido pendiente o en preparación ocupa un nodo. El espacio de las estructuras es O(n + p), más una referencia para conservar el último atendido.

## Estimación de espera

Para el ejercicio se usan duraciones fijas de **5 minutos por pedido urgente** y **10 minutos por pedido normal**. La estimación simula una preparación en serie de los pedidos pendientes, partiendo de cero y usando el orden actual de la cola.

- **Espera acumulada antes de iniciar los pedidos.** Suma lo que cada pedido espera antes de que empiece su preparación.
- **Tiempo para terminar todos los pendientes.** Suma la duración estimada de preparación de los pedidos de la cola.

Por ejemplo, con dos urgentes seguidos de dos normales, los tiempos de inicio son 0, 5, 10 y 20 minutos. La espera acumulada es **35 minutos** y se estima que el último pedido terminará a los **30 minutos**.

## Capturas de ejecución

Se registraron, en este orden, Ana (normal), Luis (urgente), Rosa (urgente) y Elena (normal). Las capturas muestran la salida de esa ejecución con las repeticiones del menú abreviadas.

**Orden, conteo y espera.** Los pendientes aparecen como 2, 3, 1 y 4. El sistema cuenta dos de cada tipo y calcula 35 minutos de espera acumulada y 30 minutos para terminar la cola.

![Captura de consola con los pedidos pendientes, el conteo y la espera estimada][captura-orden]

**Atención, finalización y cancelación.** El sistema atiende primero a Luis (#2), lo marca como completado, cancela a Elena (#4) y muestra a Luis como el último atendido.

![Captura de consola con la atención y finalización de Luis, la cancelación de Elena y la consulta del último atendido][captura-atencion]

## Conclusiones

- Separar los pedidos en dos colas FIFO permite atender primero los urgentes y conservar el orden de llegada dentro de cada prioridad.
- Mantener referencias al frente y al final permite registrar y atender pedidos en O(1). Retirar por número requiere recorrer la cola porque el número no indica la posición del nodo.
- Probar cancelaciones al inicio, en medio y al final de una cola permite comprobar que se conservan los enlaces y que la cola puede reutilizarse al quedar vacía.

[captura-orden]: capturas/orden_y_espera.png
[captura-atencion]: capturas/atencion_y_cierre.png
