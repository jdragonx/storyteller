from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips, AudioFileClip, AudioClip, concatenate_audioclips
import os
import click
from pydub import AudioSegment
from openai import OpenAI
import time
import math
from moviepy.video.fx.crop import crop

def crop_video(clip):
    # Check if the video is square
    if clip.size[0] == clip.size[1]:
        # Crop the video to 16:9 format
        new_width = clip.size[0]
        new_height = int(new_width * 9 / 16)
        clip = crop(clip, width=new_width, height=new_height, x_center=clip.size[0]/2, y_center=clip.size[1]/2)
    return clip

client = OpenAI()
max_retries = 5
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

@click.command()
@click.option('--dir', '-d', default="videos_ya_subidos", type=str, help='Directorio donde están los archivos de video')
@click.option('--output_file', '-o', type=str, help='Nombre del archivo de video de salida')
def main(dir, output_file):
    # Obtener la lista de archivos de video en el directorio
    video_files = [file for file in os.listdir(dir) if file.endswith(".mp4")]

    videos_concatenados = '\n'.join([video_file.split('#')[0].strip() for video_file in video_files])
    print("Compilando los siguientes videos:\n" + videos_concatenados)
    
    # Cargar cada video, recortar si el ratio no es el correcto, y agregar título
    video_clips = [VideoFileClip(os.path.join(dir, file)) for file in video_files]
    # video_clips = [crop_video(clip) for clip in video_clips]
    video_clips_with_titles = [add_title(clip, file.split('#')[0].strip()) for file, clip in zip(video_files, video_clips)]

    # Concatenar clips de video
    final_video = concatenate_videoclips(video_clips_with_titles)

    if not output_file:
        output_file = f"compilaciones/{video_files[0].split('#')[0].strip()}, y otros relatos de terror #terror #miedo.mp4"

    # Escribir el video final a un archivo
    final_video.write_videofile(output_file, codec='libx264', fps=24)

    # Escribir como descripcion el nombre de los videos concatenados
    descripcion_filename = f'./descripciones_historias/{output_file.split("/")[-1].replace(".mp4", ".txt")}'
    with open(descripcion_filename, 'w') as f:
        f.write(videos_concatenados)

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
                speed=0.9,
            )
            temporal_path = f".tmp/.discard/temp_audio.mp3"
            response.stream_to_file(temporal_path)
            audio = AudioSegment.from_mp3(temporal_path).apply_gain(10)

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
    # narration_path = ".tmp/.discard/narration.mp3"
    # create_narration(title_text, narration_path, voice)
    # narration_audio = AudioFileClip(narration_path)

    # Add padding of 3 seconds on each side of the narration
    silence = AudioClip(lambda t: 0, duration=2)  # 2 seconds of silence
    # padded_narration_audio = concatenate_audioclips([silence, narration_audio, silence])  # Concatenate the silence and the narration

    # total_duration = padded_narration_audio.duration
    total_duration = silence.duration

    title_clip = (TextClip(title_text, fontsize=30, color='white', bg_color='black', size=(video_clip.size[0], video_clip.size[1]))
                  .set_position(('center', 'top'))
                  .set_duration(total_duration)
                  # .set_audio(padded_narration_audio))
                  .set_audio(silence))

    return concatenate_videoclips([title_clip, video_clip])

if __name__ == '__main__':
    main()
