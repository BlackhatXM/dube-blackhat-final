import streamlit as st, tempfile, os, asyncio, subprocess
import edge_tts

st.set_page_config(page_title="DUBE BLACKHAT", page_icon="🎬")
st.title("🎬 DUBE BLACKHAT - Doblador")
st.success("✅ ONLINE - Listo para doblar")

VOCES = {
    "🇲🇽 Jorge (Hombre)": "es-MX-JorgeNeural",
    "🇲🇽 Dalia (Mujer)": "es-MX-DaliaNeural",
    "🇬🇹 Andres (Guatemala)": "es-GT-AndresNeural",
    "🇺🇸 Guy (USA)": "en-US-GuyNeural",
}

video = st.file_uploader("1. Sube tu video", type=["mp4","mov","mkv"])
texto = st.text_area("2. Escribe lo que quieres que diga:", "Hola, este es el doblaje blackhat funcionando al fin")
voz = st.selectbox("3. Elige voz", list(VOCES.keys()))

async def tts(texto, voz_id, out):
    comm = edge_tts.Communicate(texto, voz_id)
    await comm.save(out)

if video and st.button("🔥 DOBLAR AHORA", type="primary", use_container_width=True):
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in.mp4")
        audio_path = os.path.join(tmp, "voz.mp3")
        out_path = os.path.join(tmp, "out.mp4")
        with open(in_path, "wb") as f:
            f.write(video.read())

        st.info("Generando voz...")
        asyncio.run(tts(texto, VOCES[voz], audio_path))

        st.info("Pegando voz al video...")
        # Si no hay ffmpeg en streamlit, usamos solo audio
        try:
            subprocess.run(["ffmpeg","-y","-i",in_path,"-i",audio_path,"-map","0:v","-map","1:a","-c:v","copy","-shortest",out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            st.video(out_path)
            with open(out_path, "rb") as f:
                st.download_button("📥 DESCARGAR VIDEO DOBLADO", f, "doblado.mp4", use_container_width=True)
        except:
            st.audio(audio_path)
            with open(audio_path, "rb") as f:
                st.download_button("📥 DESCARGAR AUDIO DOBLADO", f, "doblado.mp3")

        st.balloons()
        st.success("¡Listo!")
