import openai
import streamlit as st

from dotenv import load_dotenv, find_dotenv
from pygments.lexers.sql import language_re

_ = load_dotenv(find_dotenv())

client = openai.OpenAI()

def transcreve_tab_mic():
    st.markdown('Transcreve microfone')

def transcreve_tab_video():
    st.markdown('Transcreve vídeo')

def transcreve_tab_audio():
    prompt_input = st.text_input('(opcional) Digite o seu prompt', key='input_audio')
    arquivo_audio = st.file_uploader('Adicione um arquivo de áudio .mp3', type=['mp3'])
    if not arquivo_audio is None:
        transcricao = client.audio.translations.create(
            model='whisper-1',
            language='pt'
        )
        st.write(transcricao)

def main():
    st.header('Bem-vindo ao Meet Transcript', divider=True)
    st.markdown('#### Transcreva áudio do microfone, de vídeo e de arquivos de áudio')
    tab_mic, tab_video, tab_audio = st.tabs(['Microfone', 'Video', 'Audio'])
    with tab_mic:
        transcreve_tab_mic()
    with tab_video:
        transcreve_tab_video()
    with tab_audio:
        transcreve_tab_audio()

if __name__ == '__main__':
    main()