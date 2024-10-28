import os
import whisperx
import json
import pandas as pd
import webvtt
import torch
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment

# Carregar o modelo do WhisperX (com checagem de CUDA usando torch)
def set_vtt(arquivo):
    """
      Alternate form to load a video dataframe via it's vtt, which can be generated previously with the whisper transcription
    """
    L = []

    for caption in webvtt.read(arquivo):
        L.append([caption.start,caption.end,str(caption.text)])

    dataframe = pd.DataFrame(L)
    return dataframe

def transcrever_audio_whisperx(file_path):
    # Transcrição com WhisperX
    print("to no whisper")
    bashCommand = "whisperx --compute_type float32 --output_format vtt " + file_path
    os.system(bashCommand)
    df = set_vtt(file_path.replace("wav", "vtt"))
    print(df)
    return df

def processar_audio(update: Update, context: CallbackContext):
    print("bbbbbbbbbbbbbb")
    audio_file = update.message.voice.get_file()
    audio_path = "audio.ogg"
    audio_file.download(audio_path)

    # Converter para WAV (necessário para o WhisperX)
    wav_path = "audio.wav"
    AudioSegment.from_ogg(audio_path).export(wav_path, format="wav")

    # Transcrever o áudio
    texto = transcrever_audio_whisperx(wav_path)
    texto_junto = ' '.join(texto[2].tolist())
    update.message.reply_text(texto_junto)

    # Remover arquivos temporários
    os.remove(audio_path)
    os.remove(wav_path)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Envie um áudio, e eu transcreverei para você!")

def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        TOKEN = config['key']
    updater = Updater(TOKEN, use_context=True)
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaa")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, processar_audio))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()