from pydub import AudioSegment
import os

#!/usr/bin/env python3
import click
from pydub import AudioSegment
import os

@click.command()
@click.option('--dir', '-d', default=1, type=str, help='Directorio donde están los archivos de audio')
@click.option('--volume', '-v', default=100, type=int, help='Volumen al cual se quiere ajustar en dB')
def main(dir, volume):
    adjust_decibels(dir, volume)

def calculate_average_decibels(folder_path):
    total_decibels = 0
    total_songs = 0

    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):  # assuming all songs are in mp3 format
            song = AudioSegment.from_mp3(os.path.join(folder_path, filename))
            total_decibels += song.dBFS
            total_songs += 1

    if total_songs == 0:
        return None  # no valid songs found in the folder

    average_decibels = total_decibels / total_songs
    return average_decibels

def adjust_decibels(folder_path, target_average_decibels):
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            song = AudioSegment.from_mp3(os.path.join(folder_path, filename))
            current_decibels = song.dBFS
            adjustment = target_average_decibels - current_decibels
            adjusted_song = song + adjustment
            adjusted_song.export(os.path.join(folder_path, f"adjusted_{filename}"), format="mp3")
