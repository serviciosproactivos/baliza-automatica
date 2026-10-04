# Baliza STT / TTS para Radioaficionados (Local & Offline)

Sistema automatizado de baliza de radio que opera de forma **100% local, offline y eficiente** en sistemas **Linux**, utilizando **Python**, **`faster-whisper`** (para reconocimiento de voz en tiempo real) y **`piper-tts`** (para síntesis de voz natural en español de Argentina).

## 🚀 Características principales
- **Reconocimiento optimizado:** Emplea `faster-whisper` con cuantización en `int8` y un contexto específico (`initial_prompt`) para capturar correctamente el alfabeto fonético internacional (OACI/NATO) y números.
- **Validación estricta de indicativos:** Verifica mediante expresiones regulares que la respuesta cumpla con el formato clásico de estaciones (2 letras, 1 número y 2 o 3 letras, ej: `LU1ABC`), traduciendo al vuelo la fonética internacional (*Lima Uniform 1...*).
- **Control interactivo por Voz:** Repite el indicativo detectado utilizando una voz natural en español argentino (Piper TTS) y solicita confirmación de lectura (`SÍ` / `NO`).
- **Registro automatizado:** Si la respuesta es afirmativa, guarda la fecha, hora y el indicativo validado en un archivo **Excel (`.xlsx`)** estructurado mediante `openpyxl`.
- **Modo de baliza dual (Configurable):** Permite reproducir un archivo de audio físico (`baliza.wav`) o generar la baliza de forma sintética mediante Text-to-Speech usando variables de entorno.

---

## 🛠️ Requisitos del Sistema (Linux, preferentemente Debian)
Asegurarse de tener instaladas las herramientas de audio del sistema (ALSA y PortAudio) antes de configurar el entorno de Python:

```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    portaudio19-dev \
    alsa-utils \
    ffmpeg \
    wget
```

---

## ⚙️ Configuración del Entorno

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/serviciosproactivos/baliza-automatica.git
   cd baliza-automatica
   ```

2. **Crear y activar un entorno virtual de Python (podría hacer falta instalar el paquete "python3-venv"):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias de Python:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🎛️ Configuración (Variables de Entorno)
Se puede crear un archivo `.env` en la raíz del proyecto o exportarlas directamente en la terminal antes de ejecutar el script:

| Variable | Descripción | Valor por defecto |
| :--- | :--- | :--- |
| `BALIZA_MODE` | Modo de baliza: `tts` (voz sintética) o `file` (archivo de audio wav) | `tts` |
| `BALIZA_TEXT` | Texto que dirá la baliza si el modo es `tts` | `"CQ. CQ. Aquí estación automática de baliza del radioclub antenita, en el marco del concurso automatizado con inteligencia artificial. Por favor, identifíquese con su señal distintiva dentro de los próximos 5 segundos, utilizando el alfabeto internacional."` |
| `AUDIO_BALIZA_FILE` | Nombre del archivo WAV si el modo es `file` | `baliza.wav` |
| `RECORD_SECONDS_CALL` | Segundos que graba para escuchar el indicativo | `4` |
| `RECORD_SECONDS_CONFIRM` | Segundos que graba para escuchar la confirmación SÍ/NO | `3` |

---

## ▶ Ejecución del Sistema

Una vez configurado, se puede iniciar la baliza directamente ejecutando:

```bash
# Ejemplo configurando variables de entorno inline
BALIZA_MODE=tts \
BALIZA_TEXT="CQ. CQ. Aquí estación automática de baliza del radioclub antenita, en el marco del concurso automatizado con inteligencia artificial. Por favor, identifíquese con su señal distintiva dentro de los próximos 5 segundos, utilizando el alfabeto internacional." \
RECORD_SECONDS_CALL=5 \
RECORD_SECONDS_CONFIRM=3 \
python3 baliza.py
```

---

## 📂 Estructura del Proyecto
```text
.
├── baliza.py             # Script principal con la lógica de baliza, STT, TTS y Excel
├── modelos_piper/        # Modelos neuronales de Piper en español de Argentina
│   ├── es_AR-daniela-high.onnx
│   └── es_AR-daniela-high.onnx.json
├── baliza.wav            # Archivo de audio opcional para modo "file"
├── requirements.txt      # Dependencias de Python
└── .gitignore            # Archivos excluidos del control de versiones
```

## 📜 Licencia
Este proyecto es de código abierto, ideal para la experimentación por parte de los queridos colegas radioaficionados.