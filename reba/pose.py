import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


PoseLandmark = vision.PoseLandmark

CONNECTIONS = vision.PoseLandmarksConnections.POSE_LANDMARKS


class PoseDetector:
    def __init__(
            self,
            model_path: str = "models/pose_landmarker_lite.task",
            num_poses: int = 1,
            min_pose_detection_confidence: float = 0.5,
            min_tracking_confidence: float = 0.5,
            ) -> None:
        #Cargando el archivo del modelo
        base_options = python.BaseOptions(model_asset_path=model_path)

        #Configuracion del modo video y cuantas personas buscar
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=num_poses,  # para REBA analizamos 1 persona
            min_pose_detection_confidence=min_pose_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        #Motor de inferencia
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        self.result = None

    def detect(self, frame, timestamp_ms: int):
        """
        Detecta la pose en un fotograma
        frame: fotograma que entrega OpenCV  (BGR)
        timestamp_ms: marca de tiempo en ms,
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        return self.result

    def get_landmarks(self, frame):
        """Devuelve los 33 landmarks como lista de puntos (x, y) en PÍXELES.

        Returns:
            Lista indexable por id de landmark, o None si no hay pose.
            Ej: puntos[14] = codo derecho en píxeles.
        """
        if not self.result or not self.result.pose_landmarks:
            return None
        height, width = frame.shape[:2]
        landmarks = self.result.pose_landmarks[0]  # primera (única) persona
        return [(int(lm.x * width), int(lm.y * height)) for lm in landmarks]

    def close(self) -> None:

        self._landmarker.close()

    def __enter__(self):
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        
        self.close()
