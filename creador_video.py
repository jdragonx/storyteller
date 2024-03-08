#!/usr/bin/env python3
from openai import OpenAI
import json
import click
import base64
import time
import math
from moviepy.editor import ImageClip, AudioFileClip, VideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.colorx import colorx
import os
import random
from pydub import AudioSegment
import itertools
import traceback
from math import sin, pi

max_retries = 100
client = OpenAI()
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

@click.command()
@click.option('--file', '-f', type=str, help='Ruta del archivo de la historia para crear el video')
@click.option('--dir', '-d', type=str, default='historias_para_video', help='Ruta del directorio de las historias para crear los videos')
@click.option('--skip-images', '-i', is_flag=True, help='No hace llamadas a la API de OpenAI para crear imágenes, todo lo requerido debe estar en la carpeta .tmp')
@click.option('--voice', '-v', type=str, default=default_voice, help='Voz a utilizar para la narración, puede ser alloy, echo, fable, onyx, nova, o shimmer')
@click.option('--create-portrait', '-p', is_flag=True, help='Crea también versiones en formato vertical de los videos')
def main(file, dir, skip_images, voice, create_portrait):
    os.makedirs('.tmp/.discard', exist_ok=True)
    os.makedirs('.tmp/audios', exist_ok=True)
    os.makedirs('.tmp/audios_con_musica', exist_ok=True)
    os.makedirs('.tmp/images', exist_ok=True)
    if file:
        try:
            create_video(file, skip_images, voice, create_portrait)
        except Exception as e:
            print(f"Error creando video para {file}: {e}. Exiting...")
            traceback.print_exc()
            return
    else:
        for file in os.listdir(dir):
            print("*" * 50)
            print(f"Creando video para {file}")
            try:
                create_video(os.path.join(dir, file), skip_images, voice, create_portrait)
            except Exception as e:
                print(f"Error creando video para {file}: {e}. Skipping...")
                traceback.print_exc()
                continue

def merge_oraciones(oraciones: list[str]):
    if len(oraciones) == 1:
        return oraciones
    merged_oraciones = []
    for i in range(len(oraciones)):
        words = oraciones[i].split()
        if len(words) <= 8:
            if i == len(oraciones) - 1:
                merged_oraciones[-1] += ' ' + oraciones[i]
            else:
                oraciones[i+1] = oraciones[i] + ' ' + oraciones[i+1]
        else:
            merged_oraciones.append(oraciones[i])
    return merged_oraciones if len(merged_oraciones) == len(oraciones) else merge_oraciones(merged_oraciones)


def create_video(file: str, skip_images: bool, voice: str, create_portrait: bool):
    with open(file, 'r') as f:
        historia = f.read()
    oraciones = [oracion.strip() for oracion in historia.split('.') if oracion.strip().replace('\n', '') != '']
    merged_oraciones = merge_oraciones(oraciones)
    
    titulo = file.split('/')[-1].split('.')[0]
    image_dir = f".tmp/images/{titulo}"
    audio_path = f".tmp/audios/{titulo}.mp3"

    if not skip_images:
        print("Creando imágenes...")
        for i, oracion in enumerate(merged_oraciones):
            get_image(historia, oracion, image_dir, i)
    
    print("Creando narracion...")
    start_times = create_narration(merged_oraciones, audio_path, voice)

    print("Creando audio...")
    create_audio(audio_path, titulo)

    print("Creando video...")
    video_path = f"videos/{titulo}.mp4"
    audio_con_musica_path = f".tmp/audios_con_musica/{titulo}.mp3"
    create_video_from_images_and_audio(image_dir, audio_con_musica_path, video_path, start_times, create_portrait)

    print("Marcando historia como terminada...")
    os.rename(file, f"historias_terminadas/{titulo}.txt")


def get_image(historia: str, oracion: str, image_dir: str, i: int):
    messages = [
        {'role': 'system', 'content': 'You are an assistant that receives a story, and a sentence extracted from it. With that you create a complete description of an image that will be used as a representation of the extracted sentence on a book. You give excruciating detail for that image description to make it convey the entire meaning of that extracted sentence according to the full context of the story. All the context and information should be contained on the image description. You should be carefull with the text used in the image description, because it might get rejected if it doesn\'t comply with the safety instructions, you should avoid any language that may include the following: "sexual", "hate", "harassment", "self-harm", "sexual/minors", "hate/threatening", "violence/graphic", "self-harm/intent", "self-harm/instructions", "harassment/threatening" or "violence". You return the response in json format, like this: {"description": "Here you put the image description"}. You always use english on the description.'},
        {'role': 'user', 'content': '{"story": "' + historia + '", "extracted_paragraph": "' + oracion + '"'},
    ]
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                response_format={"type": "json_object"},
            )
            parsed_response = json.loads(response.choices[0].message.content)
            prompt = parsed_response['description']
            moderation = client.moderations.create(input=prompt)

            while moderation.results[0].flagged:
                print("Prompt flagged by moderation. Modifying prompt...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {'role': 'system', 'content': 'You are an assistant that receives an image description that was flagged by moderation and modifies it so that is not flagged anymore and is considered safe, you should avoid any language that may include the following: "sexual", "hate", "harassment", "self-harm", "sexual/minors", "hate/threatening", "violence/graphic", "self-harm/intent", "self-harm/instructions", "harassment/threatening" or "violence". However, keep all the details of the image while avoiding the mentioned language, use synonims, contextual descriptions, modify terms, but keep the details given. You return the response in json format, like this: {"description": "Here you put the image description"}. You always use english on the description.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                parsed_response = json.loads(response.choices[0].message.content)
                prompt = parsed_response['description']
                moderation = client.moderations.create(input=prompt)

            prompt_addition = "Realistic looking image with great and perfect detail. "
            prompt = prompt_addition + prompt[:4000 - len(prompt_addition)]
            image = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format='b64_json',
            )
            b64_string = image.data[0].b64_json
            image_bytes = base64.b64decode(b64_string)
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, f'{i}.jpg')

            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            break
        except Exception as e:
            print(f"Error creating image: {e}. Retrying...")
            traceback.print_exc()
            retry_count += 1
            backoff_time = math.pow(2, retry_count)  # exponential backoff
            time.sleep(backoff_time)  # pause execution for backoff_time seconds

    if retry_count == max_retries:
        print("Max retries reached trying to create image. Exiting...")
        return None

def create_narration(oraciones: list[str], audio_path: str, voice: str):
    combined_audio = None    
    leading_silence_duration = 2000  # 2 seconds
    leading_silence = AudioSegment.silent(duration=leading_silence_duration)
    start_times = [0]  # start time of first sentence is 0

    silence_between_sentences_duration = 600  # 0.6 seconds
    silence_between_sentences = AudioSegment.silent(duration=silence_between_sentences_duration)
    total_duration = leading_silence_duration  # total duration so far

    for oracion in oraciones:
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=oracion,
                )
                temporal_path = f".tmp/.discard/temp_audio.mp3"
                response.stream_to_file(temporal_path)
                audio = AudioSegment.from_mp3(temporal_path)

                if combined_audio is None:
                    combined_audio = audio
                else:
                    combined_audio += silence_between_sentences + audio

                # add silence_between_sentences_duration and length of audio to total_duration
                total_duration += len(audio) + silence_between_sentences_duration
                
                # append total_duration to start_times as start time of next sentence
                start_times.append(total_duration)

                break
            except Exception as e:
                print(f"Error creating narration: {e}. Retrying...")
                traceback.print_exc()
                retry_count += 1
                backoff_time = math.pow(2, retry_count)  # exponential backoff
                time.sleep(backoff_time)  # pause execution for backoff_time seconds

        if retry_count == max_retries:
            print("Max retries reached. Exiting...")
            return

    combined_audio = leading_silence + combined_audio + leading_silence
    combined_audio.export(audio_path, format="mp3")

    return start_times[:-1]  # exclude the start time of the non-existent sentence after the last one

def strip_silence_from_ends(audio_segment, silence_thresh=-50):
    start_trim = detect_leading_silence(audio_segment, silence_thresh)
    end_trim = detect_leading_silence(audio_segment.reverse(), silence_thresh)

    return audio_segment[start_trim:-end_trim]

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def create_audio(audio_file_path: str, titulo: str):
    music_files = os.listdir('musicas')
    random.shuffle(music_files)
    audio = AudioSegment.from_mp3(audio_file_path).apply_gain(10)
    merged_music = strip_silence_from_ends(AudioSegment.from_mp3(f"musicas/{music_files.pop(0)}"))
    overlap_duration = 1000
    while len(merged_music) < overlap_duration:
        merged_music = strip_silence_from_ends(AudioSegment.from_mp3(f"musicas/{music_files.pop(0)}"))

    for music_file in itertools.cycle(music_files):
        music = AudioSegment.from_mp3(f"musicas/{music_file}")
        music = strip_silence_from_ends(music, silence_thresh=-20)
        try:
            merged_music = merged_music.append(music, crossfade=overlap_duration)
        except Exception as e:
            print(f"Error merging audio: {e}. Skipping...")
            traceback.print_exc()
            continue
        if len(merged_music) >= len(audio):
            break

    merged_music = merged_music.fade_in(2000).fade_out(2000)
    overlapped_audio = audio.overlay(merged_music)
    overlapped_audio.export(f".tmp/audios_con_musica/{titulo}.mp3", format='mp3')

def create_video_from_images_and_audio(image_dir: str, audio_con_musica_dir: str, video_dir: str, start_times: list[int] | None, create_portrait: bool):
    if start_times is None:
        print("No start times provided. Exiting...")
        return
    images = os.listdir(image_dir)
    images = [os.path.join(image_dir, image) for image in images]
    images = sorted(images, key=lambda x: int(x.split('/')[-1].split('.')[0]))

    # Check if there are missing images
    while len(images) < len(start_times):
        # Find the missing image number
        image_numbers = set(int(image.split('/')[-1].split('.')[0]) for image in images)
        missing_image_number = next(i for i in range(len(start_times)) if i not in image_numbers)

        # Duplicate the previous image
        previous_image = images[missing_image_number - 1]
        images.insert(missing_image_number, previous_image)
    
    images = images[:len(start_times)]  # remove extra images

    # Load the audio clip
    audio_clip = AudioFileClip(audio_con_musica_dir)

    # Calculate durations per image in seconds
    durations_per_image = [(start_times[i+1] - start_times[i])/1000 for i in range(len(start_times) - 1)]
    durations_per_image.append(audio_clip.duration - start_times[-1]/1000)  # duration of last image

    # Create a video clip from the images
    video = create_video_from_images(images, durations_per_image)

    # Set the audio of the video clip
    video = video.set_audio(audio_clip)

    # Write the result to a file
    video.write_videofile(video_dir, codec='mpeg4', fps=24, bitrate='8000k')

    if create_portrait:
        # Create a video clip from the images
        video_portrait = create_video_from_images(images, durations_per_image, ratio='portrait')
        
        # Set the audio of the video clip
        video_portrait = video_portrait.set_audio(audio_clip)

        # Write the result to 2 files
        video_portrait.write_videofile(video_dir.replace('.mp4', ' portrait.mp4'), codec='mpeg4', fps=24, bitrate='8000k')

def create_video_from_images(images: list[str], durations_per_image: list[int] | None, ratio: str = 'landscape'):
    # Create a list of clips
    clips = []
    for i, (img, dur) in enumerate(zip(images, durations_per_image)):
        interval = 3  # duration of each clip

        lightning_clips = []
        current_color = 0
        number_frames = 24
        change = 4/number_frames
        negative = True
        for j in range (number_frames):
            if negative:
                current_color = current_color - change/2
                if current_color <= -1:
                    current_color = -1
                    clip = colorx(ImageClip(img).set_duration(2), current_color)
                    lightning_clips.append(clip)
                    negative = False
                    continue
                    
            else:
                current_color = current_color + change
                if current_color >= 1:
                    current_color = 1
                    negative = True
                    
            # Create an ImageClip
            clip = colorx(ImageClip(img).set_duration(1/24), current_color)
            lightning_clips.append(clip)
        lightning = concatenate_videoclips(lightning_clips)

        # Calculate the total number of intervals
        internal_clips = []
        total_intervals = int(dur / interval) + 1
        for j in range(total_intervals):
            duration = random.uniform(2, 4)
            internal_clips.append(ImageClip(img).set_duration(duration))
            internal_clips.append(lightning)

        # Concatenate the clips to create the final clip for this image
        clip = concatenate_videoclips(internal_clips).set_duration(dur)
        clip = add_scroll_effect(clip, start_clip=i%2==0, ratio=ratio)

        clips.append(clip)

    # Return all the concatenated clips cropped to the specified ratio
    return concatenate_videoclips(clips) 

def add_scroll_effect(video: VideoClip, start_clip: bool = True, ratio: str = 'landscape') -> VideoClip:
    width, height = video.size
    if ratio == 'landscape':
        new_height = height * 9 / 16

        def scroll(get_frame, t):
            y1 = max(0, min((sin((t * pi / video.duration) + (pi/2 if start_clip else -pi/2)) + 1) / 2 * (height - new_height), height - new_height))
            y2 = y1 + new_height
            frame = get_frame(t)
            cropped_frame = VideoClip(lambda t: frame, duration=video.duration).crop(x1=0, y1=int(y1), x2=width, y2=int(y2))
            return cropped_frame.get_frame(t)

        return video.fl(lambda gf, t: scroll(gf, t))
    if ratio == 'portrait':
        new_width = width * 9 / 16

        def scroll(get_frame, t):
            x1 = max(0, min((sin((t * pi / video.duration) + (-pi/2 if start_clip else pi/2)) + 1) / 2 * (width - new_width), width - new_width))
            x2 = x1 + new_width
            frame = get_frame(t)
            cropped_frame = VideoClip(lambda t: frame, duration=video.duration).crop(x1=int(x1), y1=0, x2=int(x2), y2=height)
            return cropped_frame.get_frame(t)

        return video.fl(lambda gf, t: scroll(gf, t))

if __name__ == '__main__':
    main()