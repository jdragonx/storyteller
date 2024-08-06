#!/usr/bin/env python3
import re
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
from bing_create.main import ImageGenerator

max_retries = 100
n_imgs_per_sentence = 2
client = OpenAI()
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

cookies_bing: list = []

# Read the json file cuentas_bing.json to load the list of cookies
with open('cuentas_bing.json', 'r') as f:
    cuentas_bing = json.load(f)
    cookies_bing = cuentas_bing['cookies']

@click.command()
@click.option('--file', '-f', type=str, help='Ruta del archivo de la historia para crear el video')
@click.option('--dir', '-d', type=str, default='historias_para_video', help='Ruta del directorio de las historias para crear los videos')
@click.option('--skip-images', '-i', is_flag=True, help='No hace llamadas a la API de OpenAI para crear imágenes, todo lo requerido debe estar en la carpeta .tmp')
@click.option('--voice', '-v', type=str, default=default_voice, help='Voz a utilizar para la narración, puede ser alloy, echo, fable, onyx, nova, o shimmer, por defecto es onyx para terror y echo para cuentos')
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
        if len(words) <= 15:
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
            print(f"Ciclo de creación {i+1}/{len(merged_oraciones)}...")
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
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
            )
            parsed_response = json.loads(response.choices[0].message.content)
            prompt = parsed_response['description']
            moderation = client.moderations.create(input=prompt)

            while moderation.results[0].flagged:
                print("Prompt flagged by moderation. Modifying prompt...")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
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
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, f'{i}.jpg')

            # generate_and_save_image_openai(prompt, image_path, n_imgs)
            generate_and_save_image_bing(prompt, image_path, n_imgs_per_sentence)
            break
        except Exception as e:
            print(f"Error creating image: {e}. Retrying...")
            traceback.print_exc()
            retry_count += 1
            backoff_time = math.pow(2, retry_count)  # exponential backoff
            time.sleep(backoff_time)  # pause execution for backoff_time seconds

    if retry_count == max_retries:
        print("Max retries reached trying to create image. Duplicating last image(s)...")
        images = os.listdir(image_dir)
        images = [os.path.join(image_dir, image) for image in images]
        images = sorted(images, key=lambda x: int(x.split('/')[-1].split('.')[0]))
        for (i, image) in enumerate(images[-n_imgs_per_sentence:]):
            os.system(f'cp {image} {image.replace(".jpg", f".{i}.jpg")}')
        return None
    
def generate_and_save_image_openai(prompt: str, image_path: str, num_images: int):
    image = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=num_images,
        size="1024x1024",
        response_format='b64_json',
    )

    for (i, image_data) in enumerate(image.data):
        b64_string = image_data.b64_json
        image_bytes = base64.b64decode(b64_string)

        with open(image_path.replace('.jpg', f'.{i}.jpg'), "wb") as f:
            f.write(image_bytes)
            f.close()

def generate_and_save_image_bing(prompt: str, image_path: str, num_images: int):
    # Let's pick at random one of the cookies
    cookie = random.choice(cookies_bing)

    print(f"Usando cuenta: {cookie['cuenta']}")

    # Create an instance of the ImageGenerator class
    bing_image_generator = ImageGenerator(
        auth_cookie_u=cookie['auth_cookie_u'],
        auth_cookie_srchhpgusr=cookie['auth_cookie_srchhpgusr'],
        logging_enabled=False,
    )

    images = bing_image_generator.generate(
        prompt=prompt,
        num_images=num_images
    )

    for (i, image_link) in enumerate(images):
        response = bing_image_generator.client.get(image_link)
        if response.status_code != 200:
            raise Exception("Exception happened while saving image! (Response was not ok)")
        
        with open(image_path.replace('.jpg', f'.{i}.jpg'), "wb") as f:
            f.write(response.content)
            f.close()

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
                    speed=0.9
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

    merged_music = merged_music.fade_in(2000).fade_out(2000).apply_gain(-2)
    overlapped_audio = audio.overlay(merged_music)
    overlapped_audio.export(f".tmp/audios_con_musica/{titulo}.mp3", format='mp3')

def create_video_from_images_and_audio(image_dir: str, audio_con_musica_dir: str, video_dir: str, start_times: list[int] | None, create_portrait: bool):
    if start_times is None:
        print("No start times provided. Exiting...")
        return
    # We first check if the image dir exists, if not we try using the image dir scaping special characters
    if not os.path.exists(image_dir):
        last_folder_from_path = re.sub(r'[:",;\'`´’‘“”«»(){}\[\]¡!¿?\\/áéíóúÁÉÍÓÚñÑàèìòùäëïöüçãõâêîôû]', '', image_dir.split("/")[-1])
        image_dir = image_dir.replace(image_dir.split("/")[-1], last_folder_from_path)

    images = os.listdir(image_dir)
    images = [os.path.join(image_dir, image) for image in images]
    images = sorted(images, key=lambda x: int(x.split('/')[-1].split('.')[0]))

    # Load the audio clip
    audio_clip = AudioFileClip(audio_con_musica_dir)

    # Calculate durations per image in seconds
    durations_per_image = [(start_times[i+1] - start_times[i])/1000 for i in range(len(start_times) - 1)]
    durations_per_image.append(audio_clip.duration - start_times[-1]/1000)  # duration of last image

    new_durations_per_image = []
    current_image_number = 0
    number_of_alternatives = 0
    for image in images:
        image_number = int(image.split('/')[-1].split('.')[0])
        if current_image_number == image_number:
            number_of_alternatives += 1
        else:
            if (current_image_number >= len(durations_per_image)):
                break
            dur = durations_per_image[current_image_number] / number_of_alternatives
            for i in range(number_of_alternatives):
                new_durations_per_image.append(dur)
            current_image_number = image_number
            number_of_alternatives = 1

    if (current_image_number < len(durations_per_image)):
        dur = durations_per_image[current_image_number] / number_of_alternatives
        for i in range(number_of_alternatives):
            new_durations_per_image.append(dur)

    print(f"Images: {len(images)}, Durations: {len(new_durations_per_image)}")

    images = images[:len(new_durations_per_image)]  # remove extra images

    # Create a video clip from the images
    video = create_video_from_images(images, new_durations_per_image)

    # Set the audio of the video clip
    video = video.set_audio(audio_clip)

    # Write the result to a file
    video.write_videofile(video_dir, codec='mpeg4', fps=24, bitrate='8000k')

    if create_portrait:
        # Create a video clip from the images
        video_portrait = create_video_from_images(images, new_durations_per_image, ratio='portrait')
        
        # Set the audio of the video clip
        video_portrait = video_portrait.set_audio(audio_clip)

        # Write the result to 2 files
        video_portrait.write_videofile(video_dir.replace('.mp4', ' portrait.mp4'), codec='mpeg4', fps=24, bitrate='8000k')

def create_video_from_images(images: list[str], durations_per_image: list[int] | None, ratio: str = 'landscape'):
    # Create a list of clips
    clips = []
    for i, (img, dur) in enumerate(zip(images, durations_per_image)):
        clip = ImageClip(img).set_duration(dur)
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