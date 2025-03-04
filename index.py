from pathlib import Path

import queue
import openai
import time
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from moviepy.video.io.VideoFileClip import VideoFileClip  # Importação corrigida
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())
client = openai.OpenAI()

@st.cache_data
def get_ice_servers():
    return [{'urls': ['stun:stun.l.google.com:19302']}]

# Diretórios temporários
PASTA_TEMP = Path(__file__).parent / 'temp'
PASTA_TEMP.mkdir(exist_ok=True)
ARQUIVO_AUDIO_TEMP = PASTA_TEMP / 'audio.mp3'
ARQUIVO_VIDEO_TEMP = PASTA_TEMP / 'video.mp4'


def transcreve_tab_mic():
    webrtx_ctx = webrtc_streamer(
        key='recebe_audio',
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration={'iceServers': get_ice_servers()},
        media_stream_constraints={'video': False, 'audio': True}
    )

    if not webrtx_ctx.state.playing:
        return

    container = st.empty()
    container.markdown('Comece a falar...')
    while True:
        if webrtx_ctx.audio_receiver:
            try:
                frames_de_audio = webrtx_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                continue
            container.markdown(f'Frames recebidos {len(frames_de_audio)}')
        else:
            break


def transcreve_tab_video():
    prompt_input = st.text_input('(Opcional) Digite o seu prompt', key='input_video')
    arquivo_video = st.file_uploader('Adicione um arquivo de vídeo .mp4', type=['mp4'])

    if arquivo_video is not None:
        with open(ARQUIVO_VIDEO_TEMP, mode='wb') as video_f:
            video_f.write(arquivo_video.read())
        moviepy_video = VideoFileClip(str(ARQUIVO_VIDEO_TEMP))
        moviepy_video.audio.write_audiofile(str(ARQUIVO_AUDIO_TEMP))

        with open(ARQUIVO_AUDIO_TEMP, mode='rb') as arquivo_audio:
            transcricao = client.audio.transcriptions.create(
                model="whisper-1",
                file=arquivo_audio,
                language="pt",
                prompt=prompt_input if prompt_input else None
            )
            st.write(transcricao.text)


def transcreve_tab_audio():
    st.markdown('### Transcrever Arquivo de Áudio')

    prompt_input = st.text_input('(Opcional) Digite o seu prompt', key='input_audio')
    arquivo_audio = st.file_uploader('Adicione um arquivo de áudio (.mp3)', type=['mp3'])

    if arquivo_audio is not None:
        with st.spinner('Transcrevendo áudio...'):
            try:
                with open(ARQUIVO_AUDIO_TEMP, "wb") as f:
                    f.write(arquivo_audio.read())

                with open(ARQUIVO_AUDIO_TEMP, "rb") as audio_file:
                    transcricao = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="pt",
                        prompt=prompt_input if prompt_input else None
                    )
                st.subheader("Transcrição:")
                st.write(transcricao.text)
            except Exception as e:
                st.error(f"Erro ao processar a transcrição: {e}")


def main():
    st.header('Bem-vindo ao Meet Transcript', divider=True)
    st.markdown('#### Transcreva áudio do microfone, de vídeo e de arquivos de áudio')

    tab_mic, tab_video, tab_audio = st.tabs(['Microfone', 'Vídeo', 'Áudio'])

    with tab_mic:
        transcreve_tab_mic()

    with tab_video:
        transcreve_tab_video()

    with tab_audio:
        transcreve_tab_audio()


if __name__ == '__main__':
    main()
