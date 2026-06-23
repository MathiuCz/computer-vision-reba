"""Puntuación REBA a partir de los ángulos articulares.

Capa 4 del pipeline. Lógica pura de negocio basada en las tablas oficiales
de ergonautas (UPV): recibe ángulos en grados y devuelve la puntuación de
riesgo REBA. Sin cámara ni MediaPipe -> fácil de testear.

Tablas: https://www.ergonautas.upv.es/metodos/reba/reba-ayuda.php
"""

# =====================================================================
#  GRUPO A — puntuaciones individuales (tronco, cuello, piernas)
# =====================================================================

def puntuar_tronco(angulo):
    """Flexión del tronco (grados respecto a la vertical) -> 1 a 4."""
    if angulo < 5:        # prácticamente erguido
        return 1
    elif angulo <= 20:    # 0-20°
        return 2
    elif angulo <= 60:    # 20-60°
        return 3
    else:                 # >60°
        return 4


def puntuar_cuello(angulo):
    """Flexión del cuello (grados respecto al tronco) -> 1 a 2."""
    return 1 if angulo <= 20 else 2


def puntuar_pierna(angulo_rodilla):
    """Piernas a partir del ángulo de la rodilla (180 = recta) -> 1 a 3.

    Asumimos soporte bilateral (base 1) + modificador por flexión de rodilla.
    """
    flexion = 180 - angulo_rodilla
    puntos = 1
    if 30 <= flexion <= 60:
        puntos += 1
    elif flexion > 60:
        puntos += 2
    return puntos


# =====================================================================
#  GRUPO B — puntuaciones individuales (brazo, antebrazo, muñeca)
# =====================================================================

def puntuar_brazo(angulo):
    """Elevación del brazo respecto al tronco (0 = pegado al cuerpo) -> 1 a 4."""
    if angulo <= 20:
        return 1
    elif angulo <= 45:
        return 2
    elif angulo <= 90:
        return 3
    else:
        return 4


def puntuar_antebrazo(angulo_codo):
    """Antebrazo a partir del ángulo interno del codo (180 = estirado) -> 1 a 2.

    REBA puntúa 1 cuando la flexión está en el rango óptimo 60-100°.
    """
    flexion = 180 - angulo_codo
    return 1 if 60 <= flexion <= 100 else 2


def puntuar_muneca(angulo):
    """Flexión/extensión de la muñeca (0 = neutra) -> 1 a 2."""
    return 1 if angulo <= 15 else 2


# =====================================================================
#  TABLAS DE COMBINACIÓN (valores oficiales de ergonautas)
# =====================================================================

# Tabla A: TABLA_A[Tronco][Cuello][Piernas] -> 1-9
TABLA_A = [
    [[1, 2, 3, 4], [1, 2, 3, 4], [3, 3, 5, 6]],   # Tronco 1
    [[2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]],   # Tronco 2
    [[2, 4, 5, 6], [4, 5, 6, 7], [5, 6, 7, 8]],   # Tronco 3
    [[3, 5, 6, 7], [5, 6, 7, 8], [6, 7, 8, 9]],   # Tronco 4
    [[4, 6, 7, 8], [6, 7, 8, 9], [7, 8, 9, 9]],   # Tronco 5
]

# Tabla B: TABLA_B[Brazo][Antebrazo][Muñeca] -> 1-9
TABLA_B = [
    [[1, 2, 2], [1, 2, 3]],   # Brazo 1
    [[1, 2, 3], [2, 3, 4]],   # Brazo 2
    [[3, 4, 5], [4, 5, 5]],   # Brazo 3
    [[4, 5, 5], [5, 6, 7]],   # Brazo 4
    [[6, 7, 8], [7, 8, 8]],   # Brazo 5
    [[7, 8, 8], [8, 9, 9]],   # Brazo 6
]

# Tabla C: TABLA_C[Puntuación A][Puntuación B] -> 1-12
TABLA_C = [
    [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
    [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
    [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8],
    [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9],
    [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
    [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10],
    [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11],
    [8, 8, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11],
    [9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12],
    [10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12],
    [11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12],
    [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
]


def tabla_a(tronco, cuello, pierna):
    """Combina el Grupo A -> Puntuación A (1-9)."""
    return TABLA_A[tronco - 1][cuello - 1][pierna - 1]


def tabla_b(brazo, antebrazo, muneca):
    """Combina el Grupo B -> Puntuación B (1-9)."""
    return TABLA_B[brazo - 1][antebrazo - 1][muneca - 1]


def tabla_c(puntuacion_a, puntuacion_b):
    """Combina A y B -> Puntuación C (1-12)."""
    a = min(puntuacion_a, 12)
    b = min(puntuacion_b, 12)
    return TABLA_C[a - 1][b - 1]


# =====================================================================
#  NIVEL DE RIESGO Y ORQUESTACIÓN
# =====================================================================

def nivel_riesgo(reba):
    """Traduce la puntuación REBA final a (nivel, riesgo, actuación)."""
    if reba == 1:
        return (0, "Inapreciable", "No necesaria")
    elif reba <= 3:
        return (1, "Bajo", "Puede ser necesaria")
    elif reba <= 7:
        return (2, "Medio", "Es necesaria")
    elif reba <= 10:
        return (3, "Alto", "Cuanto antes")
    else:
        return (4, "Muy alto", "De inmediato")


def calcular_reba(angulos, lado="der", carga=0, agarre=0, actividad=0):
    """Calcula la puntuación REBA completa para un lado del cuerpo.

    Args:
        angulos: dict de calcular_angulos (grados).
        lado: "der" o "izq" (qué brazo evaluar). La selección automática por
              visibilidad es un paso posterior (ver docs/estrategia-lateralidad).
        carga: 0/1/2 (+1 si brusca). NO detectable por visión -> lo aporta el operador.
        agarre: 0/1/2/3. Tampoco detectable por visión.
        actividad: 0-3 (+1 estático, +1 repetitivo, +1 inestable).

    Returns:
        dict con el desglose: puntuacion_a/b/c, reba, nivel, riesgo, accion, lado.
    """
    # --- Grupo A (axial) ---
    # REBA da una sola puntuación de piernas: usamos la pierna en peor postura
    # (ángulo menor = más flexionada = mayor riesgo).
    peor_rodilla = min(angulos["rodilla_der"], angulos["rodilla_izq"])
    pa = tabla_a(
        puntuar_tronco(angulos["tronco"]),
        puntuar_cuello(angulos["cuello"]),
        puntuar_pierna(peor_rodilla),
    ) + carga

    # --- Grupo B (lado elegido) ---
    pb = tabla_b(
        puntuar_brazo(angulos[f"brazo_{lado}"]),
        puntuar_antebrazo(angulos[f"codo_{lado}"]),
        puntuar_muneca(angulos[f"muneca_{lado}"]),
    ) + agarre

    # --- Tabla C + actividad ---
    pc = tabla_c(pa, pb)
    reba = pc + actividad
    nivel, riesgo, accion = nivel_riesgo(reba)

    return {
        "puntuacion_a": pa,
        "puntuacion_b": pb,
        "puntuacion_c": pc,
        "reba": reba,
        "nivel": nivel,
        "riesgo": riesgo,
        "accion": accion,
        "lado": lado,
    }
