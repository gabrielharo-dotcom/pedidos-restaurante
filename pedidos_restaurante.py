"""Sistema básico de pedidos de restaurante. Ejecutar con Python 3."""

from datetime import datetime
import sys


DATOS_TIPO = {"Normal": (2, 10), "Urgente": (1, 5)}


class Pedido:
    """Guarda los datos de un pedido durante todo su ciclo."""

    def __init__(self, numero, cliente, tipo):
        # La prioridad y la duración estimada se asignan según el tipo.
        self.numero = numero
        self.cliente = cliente
        self.tipo = tipo
        self.prioridad, self.minutos = DATOS_TIPO[tipo]
        self.registrado = datetime.now()
        self.estado = "Pendiente"

    def __str__(self):
        # Se conserva la hora de registro aunque cambie el estado.
        fecha = self.registrado.strftime("%d/%m/%Y %H:%M:%S")
        return (
            f"#{self.numero} | {self.cliente} | {self.tipo} (prioridad {self.prioridad})"
            f" | {fecha} | {self.estado}"
        )


class Nodo:
    """Enlaza un pedido con el siguiente dentro de una cola."""

    def __init__(self, pedido):
        # Un nodo nuevo todavía no tiene sucesor.
        self.pedido = pedido
        self.siguiente = None


class ColaFIFO:
    """Cola enlazada con referencias al frente y al final."""

    def __init__(self):
        # Ambos extremos quedan vacíos y el contador comienza en cero.
        self.frente = None
        self.final = None
        self.cantidad = 0

    def encolar(self, pedido):
        # Anexar en el extremo final conserva el orden de llegada.
        nuevo = Nodo(pedido)
        if self.final is None:
            self.frente = nuevo
        else:
            self.final.siguiente = nuevo
        self.final = nuevo
        self.cantidad += 1

    def desencolar(self):
        # El pedido más antiguo está al frente.
        if self.frente is None:
            return None
        return self._retirar_nodo(None, self.frente)

    def retirar_por_numero(self, numero):
        # Buscar el pedido y recordar su predecesor para reconectar la cola.
        anterior = None
        actual = self.frente
        while actual is not None:
            if actual.pedido.numero == numero:
                return self._retirar_nodo(anterior, actual)
            anterior, actual = actual, actual.siguiente
        return None

    def _retirar_nodo(self, anterior, actual):
        # Actualizar los extremos si se retiró el primero o el último.
        if anterior is None:
            self.frente = actual.siguiente
        else:
            anterior.siguiente = actual.siguiente
        if self.final is actual:
            self.final = anterior
        self.cantidad -= 1
        return actual.pedido

    def __iter__(self):
        # Recorrer desde el frente sin retirar ni copiar los pedidos.
        actual = self.frente
        while actual is not None:
            yield actual.pedido
            actual = actual.siguiente


class ColaPrioridad:
    """Cola de prioridad implementada con una cola FIFO por tipo."""

    def __init__(self):
        # Las colas se inicializan en el mismo orden en que se atienden.
        self.urgentes = ColaFIFO()
        self.normales = ColaFIFO()

    def encolar(self, pedido):
        # Enviar cada pedido al final de la cola de su prioridad.
        cola = self.urgentes if pedido.prioridad == 1 else self.normales
        cola.encolar(pedido)

    def desencolar(self):
        # Usar el frente de urgentes siempre que exista.
        if self.urgentes.cantidad:
            return self.urgentes.desencolar()
        return self.normales.desencolar()

    def retirar_por_numero(self, numero):
        # El número es único, así que solo se busca en normales si hace falta.
        pedido = self.urgentes.retirar_por_numero(numero)
        if pedido is None:
            pedido = self.normales.retirar_por_numero(numero)
        return pedido

    def contar_por_tipo(self):
        # Los contadores evitan recorrer las colas para responder la consulta.
        return self.normales.cantidad, self.urgentes.cantidad

    def __iter__(self):
        # Mostrar el mismo orden que tendría la atención sucesiva.
        yield from self.urgentes
        yield from self.normales


class SistemaPedidos:
    """Coordina el registro, la atención, la preparación y las consultas."""

    def __init__(self):
        # Se generan números crecientes y se guarda el último pedido atendido.
        self.pendientes = ColaPrioridad()
        self.en_preparacion = ColaFIFO()
        self.ultimo_atendido = None
        self._siguiente_numero = 1

    def registrar(self, cliente, tipo):
        # Validar antes de registrar o consumir un número de pedido.
        cliente = cliente.strip()
        if not cliente:
            raise ValueError("El nombre del cliente no puede estar vacío.")
        if tipo not in DATOS_TIPO:
            raise ValueError("El tipo debe ser Normal o Urgente.")
        pedido = Pedido(self._siguiente_numero, cliente, tipo)
        self.pendientes.encolar(pedido)
        self._siguiente_numero += 1
        return pedido

    def atender_siguiente(self):
        # Sacar de pendientes e iniciar la preparación del pedido.
        pedido = self.pendientes.desencolar()
        if pedido is not None:
            pedido.estado = "En preparación"
            self.en_preparacion.encolar(pedido)
            self.ultimo_atendido = pedido
        return pedido

    def completar(self, numero):
        # Solo se pueden completar los pedidos que iniciaron preparación.
        pedido = self.en_preparacion.retirar_por_numero(numero)
        if pedido is not None:
            pedido.estado = "Completado"
        return pedido

    def cancelar(self, numero):
        # Solo se pueden cancelar los pedidos que aún están pendientes.
        pedido = self.pendientes.retirar_por_numero(numero)
        if pedido is not None:
            pedido.estado = "Cancelado"
        return pedido

    def estimar_espera(self):
        # Cada pedido espera la suma de las duraciones de quienes lo preceden.
        espera_acumulada = 0
        tiempo_para_terminar = 0
        for pedido in self.pendientes:
            espera_acumulada += tiempo_para_terminar
            tiempo_para_terminar += pedido.minutos
        return espera_acumulada, tiempo_para_terminar


def leer_numero():
    # Rechazar valores inválidos antes de modificar el sistema.
    try:
        numero = int(input("Número del pedido: ").strip())
        if numero > 0:
            return numero
    except ValueError:
        pass
    print("Ingresa un número de pedido entero y positivo.")
    return None


def menu():
    # Reutilizar una sola instancia durante toda la sesión de consola.
    sistema = SistemaPedidos()
    opciones = """
=== Sistema de pedidos de restaurante ===
1. Registrar pedido
2. Atender siguiente pedido
3. Marcar pedido como completado
4. Cancelar pedido pendiente
5. Ver pedidos pendientes en orden
6. Contar pedidos pendientes por tipo
7. Ver último pedido atendido
8. Calcular espera estimada
0. Salir"""
    while True:
        print(opciones)
        opcion = input("Elige una opción: ").strip()

        if opcion == "0":
            print("Sesión finalizada.")
            break
        elif opcion == "1":
            cliente = input("Cliente: ")
            tipo = input("Tipo (1. Normal / 2. Urgente): ").strip()
            if tipo not in ("1", "2"):
                print("Elige 1 para Normal o 2 para Urgente.")
                continue
            try:
                pedido = sistema.registrar(cliente, "Normal" if tipo == "1" else "Urgente")
                print(f"Registrado: {pedido}")
            except ValueError as error:
                print(error)
        elif opcion == "2":
            pedido = sistema.atender_siguiente()
            print(f"Atendido: {pedido}" if pedido else "No hay pedidos pendientes.")
        elif opcion == "3":
            if sistema.en_preparacion.cantidad == 0:
                print("No hay pedidos en preparación.")
                continue
            print("Pedidos en preparación:")
            for pedido in sistema.en_preparacion:
                print(f"  {pedido}")
            numero = leer_numero()
            if numero is not None:
                pedido = sistema.completar(numero)
                print(f"Completado: {pedido}" if pedido else "Ese pedido no está en preparación.")
        elif opcion == "4":
            numero = leer_numero()
            if numero is not None:
                pedido = sistema.cancelar(numero)
                print(f"Cancelado: {pedido}" if pedido else "Ese pedido no está pendiente.")
        elif opcion == "5":
            if not any(sistema.pendientes.contar_por_tipo()):
                print("No hay pedidos pendientes.")
                continue
            print("Pedidos pendientes en orden de atención:")
            for pedido in sistema.pendientes:
                print(f"  {pedido}")
        elif opcion == "6":
            normales, urgentes = sistema.pendientes.contar_por_tipo()
            print(f"Pendientes: {normales} normal(es) y {urgentes} urgente(s).")
        elif opcion == "7":
            pedido = sistema.ultimo_atendido
            print(f"Último atendido: {pedido}" if pedido else "Aún no se ha atendido ningún pedido.")
        elif opcion == "8":
            espera, duracion = sistema.estimar_espera()
            print(f"Espera acumulada antes de iniciar los pedidos: {espera} min.")
            print(f"Tiempo para terminar todos los pedidos pendientes: {duracion} min.")
        else:
            print("Opción inválida. Elige un número del menú.")


# Bloque de pruebas. Ejecutar: python pedidos_restaurante.py --pruebas
def ejecutar_pruebas():
    # Usar verificaciones de la biblioteca estándar sin instalar dependencias.
    import unittest

    class PruebasPedidos(unittest.TestCase):
        def test_prioridad_y_fifo_en_ambos_tipos(self):
            # Los urgentes van primero y cada tipo conserva su orden de llegada.
            sistema = SistemaPedidos()
            normal_1 = sistema.registrar("Ana", "Normal")
            urgente_1 = sistema.registrar("Luis", "Urgente")
            normal_2 = sistema.registrar("Rosa", "Normal")
            urgente_2 = sistema.registrar("Elena", "Urgente")
            orden = [urgente_1, urgente_2, normal_1, normal_2]
            self.assertEqual(list(sistema.pendientes), orden)
            self.assertEqual(sistema.pendientes.contar_por_tipo(), (2, 2))
            self.assertEqual([sistema.atender_siguiente() for _ in orden], orden)
            self.assertIs(sistema.ultimo_atendido, normal_2)
            self.assertEqual(sistema.pendientes.contar_por_tipo(), (0, 0))
            self.assertIsNone(sistema.atender_siguiente())
            self.assertIs(sistema.ultimo_atendido, normal_2)

        def test_cancelar_en_medio_en_extremos_y_reencolar(self):
            # Retirar nodos de distintas posiciones y reutilizar la cola vacía.
            sistema = SistemaPedidos()
            primero, medio, ultimo, urgente = [
                sistema.registrar(nombre, tipo)
                for nombre, tipo in [("Ana", "Normal"), ("Luis", "Normal"),
                                     ("Rosa", "Normal"), ("Elena", "Urgente")]
            ]
            for pedido in (medio, ultimo, urgente, primero):
                self.assertIs(sistema.cancelar(pedido.numero), pedido)
                self.assertEqual(pedido.estado, "Cancelado")
                self.assertIsNone(sistema.cancelar(pedido.numero))
            self.assertEqual(sistema.pendientes.contar_por_tipo(), (0, 0))
            nuevo = sistema.registrar("Emma", "Normal")
            self.assertEqual(nuevo.numero, 5)
            self.assertIs(sistema.atender_siguiente(), nuevo)

        def test_transiciones_de_estado(self):
            # Completar exige haber atendido y no se puede cancelar en preparación.
            sistema = SistemaPedidos()
            pedido = sistema.registrar("Ana", "Urgente")
            otro = sistema.registrar("Rosa", "Normal")
            self.assertIsNone(sistema.completar(pedido.numero))
            self.assertIsNone(sistema.ultimo_atendido)
            sistema.atender_siguiente()
            sistema.atender_siguiente()
            self.assertEqual(pedido.estado, "En preparación")
            self.assertIsNone(sistema.cancelar(pedido.numero))
            self.assertIs(sistema.completar(otro.numero), otro)
            self.assertIs(sistema.completar(pedido.numero), pedido)
            self.assertEqual(pedido.estado, "Completado")
            self.assertIsNone(sistema.completar(pedido.numero))
            self.assertIs(sistema.ultimo_atendido, otro)
            self.assertEqual(sistema.ultimo_atendido.estado, "Completado")
            self.assertEqual(sistema.en_preparacion.cantidad, 0)

        def test_espera_estimada_y_cola_vacia(self):
            # Con duraciones 5, 5 y 10, las esperas son 0, 5 y 10.
            sistema = SistemaPedidos()
            self.assertEqual(sistema.estimar_espera(), (0, 0))
            sistema.registrar("Ana", "Normal")
            sistema.registrar("Luis", "Urgente")
            sistema.registrar("Rosa", "Urgente")
            self.assertEqual(sistema.estimar_espera(), (15, 20))
            sistema.atender_siguiente()
            self.assertEqual(sistema.estimar_espera(), (5, 15))

        def test_registro_valido_y_datos_del_pedido(self):
            # Una entrada inválida no consume un número ni suma un pendiente.
            sistema = SistemaPedidos()
            with self.assertRaises(ValueError):
                sistema.registrar("  ", "Normal")
            with self.assertRaises(ValueError):
                sistema.registrar("Ana", "Especial")
            self.assertEqual(sistema.pendientes.contar_por_tipo(), (0, 0))
            pedido = sistema.registrar("  Ana  ", "Normal")
            self.assertEqual((pedido.numero, pedido.cliente, pedido.tipo), (1, "Ana", "Normal"))
            self.assertEqual((pedido.prioridad, pedido.estado), (2, "Pendiente"))
            self.assertIsInstance(pedido.registrado, datetime)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PruebasPedidos)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    # Elegir entre el menú normal y las pruebas con un único archivo.
    argumentos = sys.argv[1:]
    if argumentos == ["--pruebas"]:
        sys.exit(ejecutar_pruebas())
    if argumentos:
        sys.exit("Uso: python pedidos_restaurante.py [--pruebas]")
    try:
        menu()
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")
