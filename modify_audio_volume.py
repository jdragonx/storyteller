#!/usr/bin/env python3
import click
from pydub import AudioSegment
import os

@click.command()
@click.option('--dir', '-d', default=1, type=str, help='Directorio donde están los archivos de audio')
@click.option('--volume', '-v', default=-10, type=int, help='Volumen a reducir en dB')
def main(dir, volume):
    for filename in os.listdir(dir):
        if filename.endswith(".mp3"):  # assuming the audio files are in mp3 format
            audio = AudioSegment.from_mp3(os.path.join(dir, filename))
            reduced_audio = audio + volume  # reduce volume by the amount given in dB
            reduced_audio.export(os.path.join(dir, filename), format="mp3")  # save the audio file

if __name__ == '__main__':
    main()