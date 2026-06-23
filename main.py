import cv2
from reba.pose import PoseDetector
from reba.angles import calcular_angulos
from reba.scoring import calcular_reba
from reba.drawing import dibujar_esqueleto, dibujar_columna, dibujar_panel, dibujar_reba


def main() -> None:
    #Webcam por defecto , CAP_DSHOW = backend en windows
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)#abre màs rapido
    if not capture.isOpened():
        print("ERROR: no se pudo abrir la cámara. ¿Conectada o en uso por otra app?")
        return

    #FPS para el timestamp. Si la camara reporta 0, usamos 30
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_index = 0

    try:
        # 'with' garantiza que el modelo se libere al salir, pase lo que pase.
        with PoseDetector(model_path="models/pose_landmarker_full.task") as detector:
            print("Cámara abierta. Pulsa 'q' para salir.")
            while True:
                ok, frame = capture.read()
                if not ok:
                    print("ADVERTENCIA: no se pudo leer el fotograma. Cerrando.")
                    break

                frame = cv2.flip(frame, 1)  # efecto espejo (selfie)

                # Timestamp creciente que la Tasks API exige en modo VIDEO.
                timestamp_ms = int(frame_index * 1000 / fps)

                detector.detect(frame, timestamp_ms)    # 1) inferencia
                puntos = detector.get_landmarks(frame)   # landmarks en píxeles

                dibujar_esqueleto(frame, puntos)         # 2) esqueleto
                dibujar_columna(frame, puntos)           # 2b) columna (eje central)
                if puntos:
                    angulos = calcular_angulos(puntos)              # 3) ángulos REBA
                    dibujar_panel(frame, angulos)                   # 4) panel de ángulos
                    resultado = calcular_reba(angulos, lado="der")  # 5) scoring REBA
                    dibujar_reba(frame, resultado)                  # 6) puntuación en pantalla

                frame_index += 1
                frame_grande = cv2.resize(frame, None, fx=1.5, fy=1.5,  interpolation=cv2.INTER_LINEAR)

                cv2.imshow("REBA - Captura de Pose (q para salir)", frame_grande)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
