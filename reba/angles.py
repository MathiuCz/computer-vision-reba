"""
Calculo de angulos articulares a partir de landmarks de pose
Pura geometria 
"""

import numpy as np 

from reba.pose import PoseLandmark as LM


def calcular_angulo(a, b, c):
    """
Ángulo (en grados) en el vértice B, formado por los puntos A-B-C.

Ejemplo: para el codo -> A=hombro, B=codo, C=muñeca.

Args:
    a, b, c: puntos (x, y). El vértice del ángulo es b.

Returns:
    Ángulo en grados, en el rango [0, 180].
"""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    #VECTORES DE  ab y bc
    ba = a - b
    bc = c - b

    #Producto punto 
    cosine = np.dot(ba, bc)/(np.linalg.norm(ba)*np.linalg.norm(bc))

    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))) #clip seguro anti-errores de punto flotante
    return angle

def punto_medio(p1, p2):
    """Punto medio entre dos puntos (x, y). Geometría pura."""
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)


def calcular_angulos(puntos):
    """Calcula todos los ángulos REBA y los devuelve en un dict {nombre: grados}.

    Recibe la lista de landmarks en píxeles (de PoseDetector.get_landmarks).
    """
    # Centros y referencias, calculados una sola vez.
    centro_hombros = punto_medio(puntos[LM.LEFT_SHOULDER], puntos[LM.RIGHT_SHOULDER])
    centro_caderas = punto_medio(puntos[LM.LEFT_HIP], puntos[LM.RIGHT_HIP])
    cabeza = punto_medio(puntos[LM.LEFT_EAR], puntos[LM.RIGHT_EAR])
    vertical = (centro_caderas[0], centro_caderas[1] - 100)
    dir_tronco = (centro_caderas[0] - centro_hombros[0],
                  centro_caderas[1] - centro_hombros[1])

    angulos = {
        # Grupo A
        "tronco": calcular_angulo(centro_hombros, centro_caderas, vertical),
        "cuello": 180 - calcular_angulo(centro_caderas, centro_hombros, cabeza),
    }

    piernas = {
        "der": (LM.RIGHT_HIP, LM.RIGHT_KNEE, LM.RIGHT_ANKLE),
        "izq": (LM.LEFT_HIP, LM.LEFT_KNEE, LM.LEFT_ANKLE),
    }
    for lado, (cadera_id, rodilla_id, tobillo_id) in piernas.items():
        cadera = puntos[cadera_id]
        rodilla = puntos[rodilla_id]
        tobillo = puntos[tobillo_id]

        angulos[f"rodilla_{lado}"] = calcular_angulo(cadera, rodilla, tobillo) 

    # Grupo B: codo (antebrazo), brazo y muñeca, para ambos lados.
    brazos = {
        "der": (LM.RIGHT_SHOULDER, LM.RIGHT_ELBOW, LM.RIGHT_WRIST, LM.RIGHT_INDEX),
        "izq": (LM.LEFT_SHOULDER, LM.LEFT_ELBOW, LM.LEFT_WRIST, LM.LEFT_INDEX),
    }
    for lado, (hombro_id, codo_id, muneca_id, mano_id) in brazos.items():
        hombro = puntos[hombro_id]
        codo = puntos[codo_id]
        muneca = puntos[muneca_id]
        mano = puntos[mano_id]
        ref_tronco = (hombro[0] + dir_tronco[0], hombro[1] + dir_tronco[1])
        angulos[f"codo_{lado}"] = calcular_angulo(hombro, codo, muneca)
        angulos[f"brazo_{lado}"] = calcular_angulo(codo, hombro, ref_tronco)
        angulos[f"muneca_{lado}"] = 180 - calcular_angulo(codo, muneca, mano)

    return angulos





