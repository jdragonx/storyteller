from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips, AudioFileClip, AudioClip, concatenate_audioclips
import os
import click
from pydub import AudioSegment
from openai import OpenAI
import time
import math

client = OpenAI()
max_retries = 5
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

@click.command()
@click.option('--dir', '-d', default="videos_ya_subidos", type=str, help='Directorio donde están los archivos de video')
@click.option('--output_file', '-o', default="compilaciones/Compilacion.mp4", type=str, help='Nombre del archivo de video de salida')
def main(dir, output_file):
    # Obtener la lista de archivos de video en el directorio
    video_files = [file for file in os.listdir(dir) if file.endswith(".mp4")]
    
    # Cargar cada video y agregar título
    video_clips = [VideoFileClip(os.path.join(dir, file)) for file in video_files]
    video_clips_with_titles = [add_title(clip, file.split('#')[0].strip()) for file, clip in zip(video_files, video_clips)]

    # Concatenar clips de video
    final_video = concatenate_videoclips(video_clips_with_titles)

    # Escribir el video final a un archivo
    final_video.write_videofile(output_file, codec='libx264', fps=24)

def create_narration(texto, audio_path, voice: str):
    combined_audio = None
    silence = AudioSegment.silent(duration=1000)  # half a second of silence

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=texto,
            )
            temporal_path = f".tmp/.discard/temp_audio.mp3"
            response.stream_to_file(temporal_path)
            audio = AudioSegment.from_mp3(temporal_path)

            if combined_audio is None:
                combined_audio = audio
            else:
                combined_audio += silence + audio

            break
        except Exception as e:
            print(f"Error creating narration: {e}. Retrying...")
            retry_count += 1
            backoff_time = math.pow(2, retry_count)  # exponential backoff
            time.sleep(backoff_time)  # pause execution for backoff_time seconds

    if retry_count == max_retries:
        print("Max retries reached. Exiting...")
        return

    combined_audio.export(audio_path, format="mp3")

# Function to add title to a video
def add_title(video_clip, title_text, voice=default_voice):
    # Create narration for title
    narration_path = "narration.mp3"
    create_narration(title_text, narration_path, voice)
    narration_audio = AudioFileClip(narration_path)

    # Add padding of 3 seconds on each side of the narration
    silence = AudioClip(lambda t: 0, duration=1)  # Create an AudioClip of silence
    padded_narration_audio = concatenate_audioclips([silence, narration_audio, silence, silence])  # Concatenate the silence and the narration

    total_duration = padded_narration_audio.duration

    title_clip = (TextClip(title_text, fontsize=40, color='white', bg_color='black', size=(video_clip.size[0], video_clip.size[1]))
                  .set_position(('center', 'top'))
                  .set_duration(total_duration)
                  .set_audio(padded_narration_audio))  # Set the audio of the title clip to the padded narration

    return concatenate_videoclips([title_clip, video_clip])

if __name__ == '__main__':
    main()
