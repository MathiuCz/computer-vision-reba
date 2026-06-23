"""Capa de visualización del pipeline REBA.

Solo dibuja sobre el frame: esqueleto y panel de ángulos. No detecta ni
calcula — recibe datos ya listos (puntos en píxeles, dict de ángulos).
"""

import cv2

from reba.pose import CONNECTIONS, PoseLandmark as LM
from reba.angles import punto_medio


def dibujar_esqueleto(frame, puntos):
    """Dibuja el esqueleto (conexiones + articulaciones) sobre el frame.

    Args:
        frame: imagen BGR donde dibujar.
        puntos: lista de (x, y) en píxeles, o None si no hay pose.
    """
    if not puntos:
        return frame
    # Líneas primero (para que los puntos queden encima).
    for c in CONNECTIONS:
        cv2.line(frame, puntos[c.start], puntos[c.end], (255, 255, 255), 2)
    # Luego las articulaciones.
    for (cx, cy) in puntos:
        cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
    return frame


def dibujar_panel(frame, angulos):
    """Dibuja el panel de ángulos en la esquina superior izquierda.

    Args:
        frame: imagen BGR donde dibujar.
        angulos: dict {nombre: grados}.
    """
    y = 30
    for nombre, valor in angulos.items():
        cv2.putText(frame, f"{nombre}: {round(float(valor), 2)} deg", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        y += 20
    return frame


def dibujar_columna(frame, puntos):
    """Dibuja el eje central del cuerpo (columna): caderas -> hombros -> cabeza.

    MediaPipe no trae una línea central; la construimos con puntos medios.

    Args:
        frame: imagen BGR donde dibujar.
        puntos: lista de (x, y) en píxeles, o None si no hay pose.
    """
    if not puntos:
        return frame
    centro_caderas = punto_medio(puntos[LM.LEFT_HIP], puntos[LM.RIGHT_HIP])
    centro_hombros = punto_medio(puntos[LM.LEFT_SHOULDER], puntos[LM.RIGHT_SHOULDER])
    cabeza = punto_medio(puntos[LM.LEFT_EAR], puntos[LM.RIGHT_EAR])

    # Columna: caderas -> hombros (tronco) -> cabeza (cuello). Color cian (BGR).
    cv2.line(frame, centro_caderas, centro_hombros, (200, 200, 0), 3)
    cv2.line(frame, centro_hombros, cabeza, (200, 200, 0), 3)

    # Articulaciones centrales en naranja, para que resalten.
    for p in (centro_caderas, centro_hombros, cabeza):
        cv2.circle(frame, p, 5, (0, 140, 255), -1)
    return frame


# Color por nivel de riesgo REBA (BGR): de verde (bajo) a rojo (muy alto).
_COLOR_RIESGO = {
    0: (0, 180, 0),     # inapreciable
    1: (0, 200, 120),   # bajo
    2: (0, 190, 255),   # medio
    3: (0, 100, 255),   # alto
    4: (0, 0, 255),     # muy alto
}


def dibujar_reba(frame, resultado):
    """Dibuja la puntuación REBA con color según el nivel de riesgo.

    Args:
        frame: imagen BGR donde dibujar.
        resultado: dict que devuelve scoring.calcular_reba.
    """
    color = _COLOR_RIESGO.get(resultado["nivel"], (255, 255, 255))
    texto = f"REBA {resultado['reba']} - {resultado['riesgo']} [{resultado['lado']}]"

    w = frame.shape[1]
    # Fondo oscuro para que el texto se lea sobre cualquier imagen.
    cv2.rectangle(frame, (w - 340, 10), (w - 10, 48), (0, 0, 0), -1)
    cv2.putText(frame, texto, (w - 330, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame
