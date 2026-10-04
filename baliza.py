import time
import datetime
import os
import re
import wave
import numpy as np
import pyaudio
import pandas as pd
from faster_whisper import WhisperModel
from piper import PiperVoice, SynthesisConfig

# --- CONFIGURACIÓN & VARIABLES DE ENTORNO ---
AUDIO_BALIZA = os.getenv("AUDIO_BALIZA_FILE", "baliza.wav")       
MODEL_SIZE = "base"
RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
EXCEL_FILE = "registro_baliza.xlsx"

# Modo de baliza: "file" o "tts"
BALIZA_MODE = os.getenv("BALIZA_MODE", "tts").lower()
BALIZA_TEXT = os.getenv("BALIZA_TEXT", "CQ. CQ. Aquí estación automática de baliza del radioclub antenita, en el marco del concurso robótico. Por favor, identifíquese con su señal distintiva dentro de los próximos 5 segundos, utilizando el alfabeto internacional.")

# Tiempos de grabación configurables
RECORD_SECONDS_CALL = int(os.getenv("RECORD_SECONDS_CALL", 6))
RECORD_SECONDS_CONFIRM = int(os.getenv("RECORD_SECONDS_CONFIRM", 3))

print(f"[i] Configuración del sistema cargada:")
print(f"    - Modo de baliza: {BALIZA_MODE}")
if BALIZA_MODE == "tts":
    print(f"    - Texto de baliza TTS: '{BALIZA_TEXT}'")
print(f"    - Tiempo grabación de llamada: {RECORD_SECONDS_CALL}s")
print(f"    - Tiempo grabación de confirmación: {RECORD_SECONDS_CONFIRM}s")

# Rutas del modelo Piper en Español de Argentina (Daniela)
PIPER_MODEL_PATH = "modelos_piper/es_AR-daniela-high.onnx"
PIPER_CONFIG_PATH = "modelos_piper/es_AR-daniela-high.onnx.json"

# PIPER_MODEL_PATH = "modelos_piper/es_MX-claude-high.onnx"
# PIPER_CONFIG_PATH = "modelos_piper/es_MX-claude-high.onnx.json"

RADIO_CONTEXT = (
    "QSO, CQ, DX, QTH, QSL, "
    "Alfa, Alpha, América, Argentina, "
    "Bravo, Boston, Brasil, "
    "Charlie, Canadá, "
    "Delta, Dinamarca, "
    "Echo, Eko, Edison, España, "
    "Foxtrot, Francia, "
    "Golf, Guatemala, "
    "Hotel, Habana, "
    "India, Italia, "
    "Juliett, Juliet, Japón, "
    "Kilo, Kilowatt, "
    "Lima, Londres, "
    "Mike, Madrid, México, "
    "November, Noviembre, Nicaragua, Noruega, "
    "Oscar, Oslo, Ontario, "
    "Papa, Portugal, París, "
    "Quebec, Quito, "
    "Romeo, Roma, "
    "Sierra, Santiago, "
    "Tango, Tokio, "
    "Uniform, Unión, Uruguay, "
    "Victor, Victoria, Valencia, Venezuela, "
    "Whiskey, Wisqui, Washington, Walter, "
    "X-ray, Xray, Equis, Xilófono, "
    "Yankee, Yanki, Yokohama, "
    "Zulu, Zúrich, Zaragoza. "
    "0 1 2 3 4 5 6 7 8 9."
)

# Diccionarios de fonética
FONETICA_MAP = {
    "ALFA": "A", "ALPHA": "A", "ARGENTINA": "A", "AMÉRICA": "A",
    "BRAVO": "B", "BOSTON": "B",
    "CHARLIE": "C", "CANADÁ": "C",
    "DELTA": "D", "DINAMARCA": "D",
    "ECHO": "E", "EKO": "E", "ESPAÑA": "E", "EDISON": "E",
    "FOXTROT": "F", "FRANCIA": "F",
    "GOLF": "G", "GUATEMALA": "G",
    "HOTEL": "H", "HABANA": "H",
    "INDIA": "I", "ITALIA": "I",
    "JULIETT": "J", "JULIET": "J", "JAPÓN": "J",
    "KILO": "K", "KILOWATT": "K",
    "LIMA": "L", "LONDRES": "L",
    "MIKE": "M", "MÉXICO": "M", "MADRID": "M",
    "NOVEMBER": "N", "NOVIEMBRE": "N", "NORUEGA": "N", "NICARAGUA": "N",
    "OSCAR": "O", "ONTARIO": "O", "OSLO": "O",
    "PAPA": "P", "PORTUGAL": "P", "PARÍS": "P",
    "QUEBEC": "Q", "QUITO": "Q",
    "ROMEO": "R", "ROMA": "R",
    "SIERRA": "S", "SANTIAGO": "S",
    "TANGO": "T", "TOKIO": "T",
    "UNIFORM": "U", "UNIÓN": "U", "URUGUAY": "U",
    "VÍCTOR": "V", "VALENCIA": "V", "VENEZUELA": "V", "VICTORIA": "V",
    "WHISKEY": "W", "WISQUI": "W", "WASHINGTON": "W", "WALTER": "W",
    "XRAY": "X", "EQUIS": "X", "XILOFÓN": "X", "SILOFÓN": "X", "XILÓFONO": "X",
    "YANKEE": "Y", "YANKI": "Y", "YOKOHAMA": "Y",
    "ZULU": "Z", "SOLO": "Z", "ZURICH": "Z", "ZARAGOZA": "Z",
    "CERO": "0", "UNO": "1", "DOS": "2", "TRES": "3", "CUATRO": "4",
    "CINCO": "5", "SEIS": "6", "SIETE": "7", "OCHO": "8", "NUEVE": "9"
}

LETRA_A_FONETICA = {
    'A': 'Alfa', 'B': 'Bravo', 'C': 'Charly', 'D': 'Delta', 'E': 'Eko',
    'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliet',
    'K': 'Kilo', 'L': 'Lima', 'M': 'Maik', 'N': 'November', 'O': 'Oscar',
    'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor', 'W': 'Whisky', 'X': 'X-ray', 'Y': 'Yanki',
    'Z': 'Zulu',
    '0': 'cero', '1': 'uno', '2': 'dos', '3': 'tres', '4': 'cuatro',
    '5': 'cinco', '6': 'seis', '7': 'siete', '8': 'ocho', '9': 'nueve'
}

print("Cargando modelo Whisper...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("Cargando modelo Piper TTS (Español Argentina)...")
piper_voice = PiperVoice.load(PIPER_MODEL_PATH, config_path=PIPER_CONFIG_PATH)

p = pyaudio.PyAudio()

def hablar_texto_piper(texto):
    syn_config = SynthesisConfig(length_scale=1.2)
    print(f"[Voz Argentina Piper]: {texto}")
    output_wav = "temp_output.wav"
    with wave.open(output_wav, "wb") as wav_file:
        piper_voice.synthesize_wav(texto, wav_file, syn_config=syn_config)
    os.system(f"aplay {output_wav} > /dev/null 2>&1")
    if os.path.exists(output_wav):
        os.remove(output_wav)

def ejecutar_baliza():
    """Ejecuta la baliza según la configuración (archivo físico o TTS)"""
    if BALIZA_MODE == "file":
        if not os.path.exists(AUDIO_BALIZA):
            print(f"[!] Error: El archivo de baliza '{AUDIO_BALIZA}' no existe.")
            return False
        print(f"[>] Reproduciendo archivo de baliza: {AUDIO_BALIZA}")
        os.system(f"aplay {AUDIO_BALIZA} > /dev/null 2>&1 || ffplay -nodisp -autoexit {AUDIO_BALIZA} > /dev/null 2>&1")
    else:
        # Modo TTS por defecto
        hablar_texto_piper(BALIZA_TEXT)
    return True

def convertir_a_fonetica_hablada(licencia):
    palabras_habladas = []
    for char in licencia:
        if char in LETRA_A_FONETICA:
            palabras_habladas.append(LETRA_A_FONETICA[char])
    return " ".join(palabras_habladas)

def grabar_audio(segundos):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * segundos)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    
    audio_data = b''.join(frames)
    return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

def decodificar_fonetica_a_indicativo(texto):
    palabras = re.findall(r'\b\w+\b', texto.upper())
    resultado_letras = []
    for palabra in palabras:
        if palabra in FONETICA_MAP:
            resultado_letras.append(FONETICA_MAP[palabra])
        elif palabra.isdigit():
            resultado_letras.append(palabra)
        elif len(palabra) == 1 and palabra.isalpha():
            resultado_letras.append(palabra)

    indicativo_armado = "".join(resultado_letras)
    patron = r'^[A-Z]{2}[0-9][A-Z]{2,3}$'
    
    if re.match(patron, indicativo_armado):
        return indicativo_armado
    return None

def guardar_en_excel(licencia):
    ahora = datetime.datetime.now()
    nueva_fila = {
        "Fecha": [ahora.strftime("%Y-%m-%d")],
        "Hora": [ahora.strftime("%H:%M:%S")],
        "Licencia Válida": [licencia],
        "Estado": ["Confirmado (SI)"]
    }
    df_nuevo = pd.DataFrame(nueva_fila)
    if os.path.exists(EXCEL_FILE):
        df_existente = pd.read_excel(EXCEL_FILE)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo

    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='QSO Baliza')
    print(f"[✔] Licencia {licencia} guardada en {EXCEL_FILE}")

# --- CICLO DE LA BALIZA ---
def ciclo_baliza():
    print("\n--- CICLO DE BALIZA INICIADO ---")
    
    # 1. Ejecutar baliza (Archivo o TTS)
    exito = ejecutar_baliza()
    if not exito:
        return
    
    # 2. Grabar respuesta del corresponsal
    print(f"[*] Grabando llamada del corresponsal ({RECORD_SECONDS_CALL}s)...")
    audio_np = grabar_audio(segundos=RECORD_SECONDS_CALL)

    segments, _ = model.transcribe(
        audio_np, beam_size=1, language="es", 
        initial_prompt=RADIO_CONTEXT, condition_on_previous_text=False
    )
    texto_entendido = "".join([s.text for s in segments]).strip()

    if not texto_entendido:
        print("[!] No se detectó voz.")
        hablar_texto_piper("No se ha recibido ninguna señal distintiva.")
        return

    print(f"> Transcripción fonética cruda: '{texto_entendido}'")

    licencia_valida = decodificar_fonetica_a_indicativo(texto_entendido)

    if not licencia_valida:
        print("[!] La fonética interpretada no coincide con un indicativo válido.")
        hablar_texto_piper("No se ha recibido ninguna señal distintiva, o la licencia no pudo ser interpretada correctamente.")
        return

    print(f"[✔] Indicativo decodificado correctamente: {licencia_valida}")

    licencia_fonetica_hablada = convertir_a_fonetica_hablada(licencia_valida)
    print(f"> Deletreo internacional: {licencia_fonetica_hablada}")

    hablar_texto_piper(f"La licencia detectada fue: {licencia_fonetica_hablada}. ¿Es correcta?. Por favor responda diciendo sí o no dentro de los próximos tres segundos.")

    print(f"[*] Esperando confirmación SÍ / NO ({RECORD_SECONDS_CONFIRM}s)...")
    audio_confirmacion = grabar_audio(segundos=RECORD_SECONDS_CONFIRM)

    segments_conf, _ = model.transcribe(
        audio_confirmacion, beam_size=1, language="es", condition_on_previous_text=False
    )
    respuesta_confirmacion = "".join([s.text for s in segments_conf]).strip().upper()
    print(f"> Confirmación: '{respuesta_confirmacion}'")

    if "SÍ" in respuesta_confirmacion or "SI" in respuesta_confirmacion or "CORRECTO" in respuesta_confirmacion or "AFIRMA" in respuesta_confirmacion or "AFIRMATIVO" in respuesta_confirmacion or "POSITIVO" in respuesta_confirmacion:
        print("[✔] Confirmación positiva. Guardando...")
        hablar_texto_piper("Su licencia ha sido registrada correctamente. ¡Gracias por el contacto!")
        guardar_en_excel(licencia_valida)
    else:
        print("[✘] Confirmación negativa. Descartando.")
        hablar_texto_piper("La licencia detectada ha sido descartada. Por favor vuelva a intentarlo. ¡Gracias!")

if __name__ == "__main__":
    try:
        while True:
            ciclo_baliza()
            print("\nPróximo ciclo en 10 segundos...\n")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nBaliza detenida.")
        p.terminate()