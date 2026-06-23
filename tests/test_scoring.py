"""Tests unitarios del motor de scoring REBA.

Lógica pura -> rápida de testear y sin dependencias de cámara/MediaPipe.
Ejecutar con:  uv run pytest
"""

from reba.scoring import (
    puntuar_tronco, puntuar_cuello, puntuar_pierna,
    puntuar_brazo, puntuar_antebrazo, puntuar_muneca,
    tabla_a, tabla_b, tabla_c, nivel_riesgo, calcular_reba,
)


# --- Puntuaciones individuales (rangos de grados) ---

def test_puntuar_tronco():
    assert puntuar_tronco(0) == 1
    assert puntuar_tronco(10) == 2
    assert puntuar_tronco(45) == 3
    assert puntuar_tronco(70) == 4


def test_puntuar_cuello():
    assert puntuar_cuello(10) == 1
    assert puntuar_cuello(25) == 2


def test_puntuar_pierna():
    assert puntuar_pierna(180) == 1   # recta
    assert puntuar_pierna(140) == 2   # flexión 40° (30-60)
    assert puntuar_pierna(100) == 3   # flexión 80° (>60)


def test_puntuar_brazo():
    assert puntuar_brazo(10) == 1
    assert puntuar_brazo(30) == 2
    assert puntuar_brazo(70) == 3
    assert puntuar_brazo(100) == 4


def test_puntuar_antebrazo():
    assert puntuar_antebrazo(100) == 1   # flexión 80° (rango óptimo)
    assert puntuar_antebrazo(180) == 2   # estirado, flexión 0°


def test_puntuar_muneca():
    assert puntuar_muneca(10) == 1
    assert puntuar_muneca(20) == 2


# --- Tablas (valores oficiales de ergonautas) ---

def test_tabla_a():
    assert tabla_a(1, 1, 1) == 1
    assert tabla_a(5, 3, 4) == 9


def test_tabla_b():
    assert tabla_b(1, 1, 1) == 1
    assert tabla_b(6, 2, 3) == 9


def test_tabla_c():
    assert tabla_c(1, 1) == 1
    assert tabla_c(12, 12) == 12
    assert tabla_c(5, 4) == 5


def test_nivel_riesgo():
    assert nivel_riesgo(1)[1] == "Inapreciable"
    assert nivel_riesgo(3)[1] == "Bajo"
    assert nivel_riesgo(7)[1] == "Medio"
    assert nivel_riesgo(10)[1] == "Alto"
    assert nivel_riesgo(12)[1] == "Muy alto"


# --- Orquestación y principio de lateralidad ---

_ANGULOS = {
    "tronco": 50, "cuello": 25,
    # Dos rodillas (como las da calcular_angulos). El scoring usa la peor
    # (ángulo menor); aquí la peor es 150 -> mismo resultado que antes.
    "rodilla_der": 150, "rodilla_izq": 170,
    "brazo_der": 80, "codo_der": 100, "muneca_der": 20,
    "brazo_izq": 10, "codo_izq": 95, "muneca_izq": 5,
}


def test_calcular_reba_caso_completo():
    r = calcular_reba(_ANGULOS, lado="der")
    assert r["reba"] == 5
    assert r["riesgo"] == "Medio"


def test_grupo_a_comun_grupo_b_varia():
    """El Grupo A (axial) es igual en ambos lados; el Grupo B cambia.

    Verifica el principio REBA: nunca se promedian los lados.
    """
    der = calcular_reba(_ANGULOS, lado="der")
    izq = calcular_reba(_ANGULOS, lado="izq")
    assert der["puntuacion_a"] == izq["puntuacion_a"]   # axial -> común
    assert der["puntuacion_b"] != izq["puntuacion_b"]   # bilateral -> distinto


def test_carga_suma_a_grupo_a():
    base = calcular_reba(_ANGULOS, lado="der")
    con_carga = calcular_reba(_ANGULOS, lado="der", carga=2)
    assert con_carga["puntuacion_a"] == base["puntuacion_a"] + 2
