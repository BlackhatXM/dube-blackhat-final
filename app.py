import streamlit as st, tempfile, os, asyncio, subprocess
import speech_recognition as sr
import edge_tts

st.set_page_config(page_title="DUBE BLACKHAT", page_icon="🎬")
st.title("🎬 DUBE BLACKHAT")
st.success("✅ Servidor listo")

VOCES = {
    "MX Jorge": "es-MX-JorgeNeural",
    "MX Dalia": "es-MX-DaliaNeural", 
    "GT Andres": "es-GT-AndresNeural"
}

video = st.file_uploader("Sube video MP4", type=["mp4","mov","mp3","wav"])
voz_sel = st.selectbox("Voz doblaje", list(VOCES.keys()))
texto_forzado = st.text_area("Si no detecta audio, escribe aquí el texto a doblar:", "")

async def hacer_tts(texto, voz_id, out):
    await edge_tts.Communicate(texto, voz_id).save(out)

if video and st.button("DOBLAR AHORA 🔥", type="primary", use_container_width=True):
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in.mp4")
        wav_path = os.path.join(tmp, "audio.wav")
        dubbed_path = os.path.join(tmp, "dubbed.mp3")
        out_path = os.path.join(tmp, "out.mp4")
        
        with open(in_path, "wb") as f:
            f.write(video.read())
        
        st.info("Extrayendo audio...")
        subprocess.run(["ffmpeg","-i",in_path,"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",wav_path,"-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        texto = ""
        if not texto_forzado:
            try:
                st.info("Transcribiendo (gratis)...")
                r = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio = r.record(source)
                texto = r.recognize_google(audio, language="es-GT")
                st.success(f"Detectado: {texto}")
            except Exception as e:
                st.warning(f"No se detectó voz clara: {e}. Usa el texto manual de arriba.")
                texto = texto_forzado
        else:
            texto = texto_forzado

        if texto:
            st.info("Generando doblaje...")
            asyncio.run(hacer_tts(texto, VOCES[voz_sel], dubbed_path))
            subprocess.run(["ffmpeg","-i",in_path,"-i",dubbed_path,"-map","0:v","-map","1:a","-c:v","copy","-shortest",out_path,"-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            st.balloons()
            st.video(out_path)
            with open(out_path, "rb") as f:
                st.download_button("📥 DESCARGAR", f, file_name="doblado.mp4", use_container_width=True)
