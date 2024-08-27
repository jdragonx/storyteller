from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips, AudioClip
import os
import click

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

# Function to add title to a video
def add_title(video_clip, title_text):
    silence = AudioClip(lambda t: 0, duration=2)  # 2 seconds of silence
    total_duration = silence.duration

    title_clip = (TextClip(title_text, fontsize=30, color='white', bg_color='black', size=(video_clip.size[0], video_clip.size[1]))
                  .set_position(('center', 'top'))
                  .set_duration(total_duration)
                  # .set_audio(padded_narration_audio))
                  .set_audio(silence))

    return concatenate_videoclips([title_clip, video_clip])

if __name__ == '__main__':
    main()
