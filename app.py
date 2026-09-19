import streamlit as st
import tempfile
import os
import asyncio
import subprocess
import whisper
import edge_tts

st.set_page_config(page_title="DUBE BLACKHAT", page_icon="🎬")
st.title("🎬 DUBE BLACKHAT - Doblador")
st.write("Sube tu video y lo doblamos al idioma que quieras")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

VOCES = {
    "Español MX - Jorge (Hombre)": "es-MX-JorgeNeural",
    "Español MX - Dalia (Mujer)": "es-MX-DaliaNeural",
    "Inglés USA - Guy": "en-US-GuyNeural",
    "Inglés USA - Jenny": "en-US-JennyNeural",
}

video = st.file_uploader("Sube video MP4", type=["mp4","mov","mkv","mp3"])
voz = st.selectbox("Elige voz doblada", list(VOCES.keys()))

async def tts(texto, voz_id, out):
    com = edge_tts.Communicate(texto, voz_id)
    await com.save(out)

if video and st.button("DOBLAR AHORA", type="primary", use_container_width=True):
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in.mp4")
        audio_path = os.path.join(tmp, "audio.wav")
        dubbed_audio = os.path.join(tmp, "dubbed.mp3")
        out_path = os.path.join(tmp, "out.mp4")

        with open(in_path, "wb") as f:
            f.write(video.read())

        st.info("1/4 Extrayendo audio...")
        subprocess.run(["ffmpeg","-i",in_path,"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",audio_path,"-y"], check=True)

        st.info("2/4 Transcribiendo...")
        result = model.transcribe(audio_path, fp16=False)
        texto = result["text"]
        st.success(f"Texto detectado: {texto}")

        st.info("3/4 Generando voz doblada...")
        asyncio.run(tts(texto, VOCES[voz], dubbed_audio))

        st.info("4/4 Creando video final...")
        subprocess.run(["ffmpeg","-i",in_path,"-i",dubbed_audio,"-map","0:v","-map","1:a","-c:v","copy","-shortest",out_path,"-y"], check=True)

        st.balloons()
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("📥 DESCARGAR VIDEO DOBLADO", f, "video_doblado.mp4", use_container_width=True)
