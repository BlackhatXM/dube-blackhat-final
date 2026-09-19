import streamlit as st
import tempfile, os, asyncio, subprocess
from faster_whisper import WhisperModel
import edge_tts

st.set_page_config(page_title="DUBE BLACKHAT", page_icon="🎬")
st.title("🎬 DUBE BLACKHAT - Doblador")
st.write("Sube tu video y lo doblamos")

@st.cache_resource
def load_model():
    return WhisperModel("base", device="cpu", compute_type="int8")

model = load_model()

VOCES = {
    "Español MX - Jorge": "es-MX-JorgeNeural",
    "Español MX - Dalia": "es-MX-DaliaNeural",
    "Inglés USA - Guy": "en-US-GuyNeural",
    "Inglés USA - Jenny": "en-US-JennyNeural",
}

video = st.file_uploader("Sube video MP4", type=["mp4","mov","mkv","mp3"])
voz = st.selectbox("Elige voz", list(VOCES.keys()))

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
        segments, info = model.transcribe(audio_path)
        texto = " ".join([s.text for s in segments])
        st.success(f"Texto: {texto}")

        st.info("3/4 Generando voz...")
        asyncio.run(tts(texto, VOCES[voz], dubbed_audio))

        st.info("4/4 Creando video...")
        subprocess.run(["ffmpeg","-i",in_path,"-i",dubbed_audio,"-map","0:v","-map","1:a","-c:v","copy","-shortest",out_path,"-y"], check=True)

        st.balloons()
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("📥 DESCARGAR", f, "doblado.mp4", use_container_width=True)
