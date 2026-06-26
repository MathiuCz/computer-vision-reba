# 🦴 Computer Vision REBA

**Evaluación ergonómica REBA en tiempo real mediante visión por computadora.**

Analiza la postura de un trabajador a través de la webcam y calcula automáticamente la puntuación [REBA (Rapid Entire Body Assessment)](https://www.ergonautas.upv.es/metodos/reba/reba-ayuda.php), mostrando el nivel de riesgo ergonómico en pantalla.

---

## ✨ Características

- 🎥 **Captura en tiempo real** — Análisis de postura directamente desde la webcam.
- 🤖 **Detección de pose con MediaPipe** — Usa el modelo `PoseLandmarker` de Google para detectar 33 puntos articulares.
- 📐 **Cálculo de ángulos articulares** — Geometría vectorial pura para obtener ángulos de tronco, cuello, rodillas, brazos, codos y muñecas.
- 📊 **Scoring REBA completo** — Tablas oficiales de [Ergonautas (UPV)](https://www.ergonautas.upv.es/metodos/reba/reba-ayuda.php): Grupo A (tronco, cuello, piernas), Grupo B (brazo, antebrazo, muñeca), Tabla C y nivel de riesgo.
- 🎨 **Visualización en pantalla** — Esqueleto, columna vertebral (eje central), panel de ángulos y puntuación REBA con código de color por riesgo.
- 🧪 **Tests unitarios** — El motor de scoring es lógica pura sin dependencias de cámara, fácil de verificar.

---

## 📁 Estructura del Proyecto

```
computer_vision_REBA/
├── main.py                  # Punto de entrada: pipeline completo con webcam
├── pyproject.toml           # Configuración del proyecto y dependencias
├── models/
│   ├── pose_landmarker_full.task   # Modelo MediaPipe (precisión alta)
│   └── pose_landmarker_lite.task   # Modelo MediaPipe (ligero)
├── reba/
│   ├── __init__.py
│   ├── pose.py              # Capa 1: Detección de pose (MediaPipe wrapper)
│   ├── angles.py            # Capa 2: Cálculo de ángulos articulares
│   ├── scoring.py           # Capa 3: Motor de puntuación REBA
│   └── drawing.py           # Capa 4: Visualización (esqueleto, panel, REBA)
└── tests/
    └── test_scoring.py      # Tests unitarios del motor de scoring
```

---

## 🏗️ Arquitectura (Pipeline)

El sistema sigue un pipeline de 4 capas, donde cada módulo tiene una responsabilidad clara:

```
Webcam → [pose.py] → [angles.py] → [scoring.py] → [drawing.py] → Pantalla
          Detectar     Calcular       Puntuar        Dibujar
          landmarks    ángulos        REBA           resultado
```

| Capa | Módulo | Responsabilidad |
|------|--------|-----------------|
| 1 | `pose.py` | Inferencia de MediaPipe → 33 landmarks en píxeles |
| 2 | `angles.py` | Geometría vectorial → ángulos articulares en grados |
| 3 | `scoring.py` | Tablas REBA oficiales → puntuación y nivel de riesgo |
| 4 | `drawing.py` | Renderizado → esqueleto, panel de ángulos y score REBA |

---

## 🚀 Instalación

### Prerrequisitos

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (gestor de paquetes recomendado)
- **Webcam** conectada

### Pasos

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/MathiuCz/computer-vision-reba.git
   cd computer-vision-reba
   ```

2. **Instalar dependencias con uv:**

   ```bash
   uv sync
   ```

   > Si prefieres pip:
   > ```bash
   > python -m venv .venv
   > .venv\Scripts\activate    # Windows
   > # source .venv/bin/activate  # Linux/macOS
   > pip install mediapipe numpy opencv-python
   > ```

3. **Ejecutar:**

   ```bash
   uv run python main.py
   ```

---

## 🎮 Uso

Al ejecutar `main.py`, se abre la webcam y se muestra:

- **Esqueleto** — Conexiones y articulaciones en verde/blanco.
- **Columna vertebral** — Eje central (caderas → hombros → cabeza) en cian.
- **Panel de ángulos** — Esquina superior izquierda, cada articulación en grados.
- **Puntuación REBA** — Esquina superior derecha, con color según el riesgo.

**Controles:**
- Pulsa **`q`** para salir.

---

## 📊 Niveles de Riesgo REBA

| Puntuación | Nivel | Riesgo | Actuación |
|:----------:|:-----:|--------|-----------|
| 1 | 0 | 🟢 Inapreciable | No necesaria |
| 2 – 3 | 1 | 🟡 Bajo | Puede ser necesaria |
| 4 – 7 | 2 | 🟠 Medio | Es necesaria |
| 8 – 10 | 3 | 🔴 Alto | Cuanto antes |
| 11 – 12+ | 4 | 🔴 Muy alto | De inmediato |

---

## 🧪 Tests

El motor de scoring (`scoring.py`) es lógica pura sin dependencias de cámara ni MediaPipe, lo que permite tests rápidos y determinísticos:

```bash
uv run pytest
```

Los tests verifican:
- Rangos de puntuación individual (tronco, cuello, piernas, brazo, antebrazo, muñeca).
- Tablas de combinación A, B y C contra valores oficiales.
- Niveles de riesgo.
- Orquestación completa con lateralidad (brazo derecho vs. izquierdo).
- Correcta aplicación del modificador de carga.

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) | Detección de pose (33 landmarks) |
| [OpenCV](https://opencv.org/) | Captura de webcam y visualización |
| [NumPy](https://numpy.org/) | Cálculo vectorial de ángulos |
| [pytest](https://pytest.org/) | Tests unitarios |
| [uv](https://docs.astral.sh/uv/) | Gestión de dependencias |

---

## 📝 Notas

- **Lateralidad:** El sistema evalúa un lado a la vez (`"der"` o `"izq"`). Por defecto se analiza el lado derecho. Para las piernas, siempre se usa la de peor postura (mayor riesgo).
- **Parámetros manuales:** Los factores de carga, agarre y actividad no son detectables por visión, por lo que se configuran como argumentos en `calcular_reba()`.
- **Modelos incluidos:** El directorio `models/` contiene dos variantes del modelo de pose de MediaPipe (`full` para mayor precisión y `lite` para menor latencia).

---

## 📄 Licencia

Este proyecto es de código abierto. Consulta el archivo `LICENSE` para más detalles.

---

## 🔗 Referencias

- [Método REBA — Ergonautas (UPV)](https://www.ergonautas.upv.es/metodos/reba/reba-ayuda.php)
- [MediaPipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)
