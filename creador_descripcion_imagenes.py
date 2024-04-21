#!/usr/bin/env python3
import pickle
from openai import OpenAI
import json
import click
import time
import math
import os
import traceback

max_retries = 100
client = OpenAI()
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

@click.command()
@click.option('--file', '-f', type=str, help='Ruta del archivo de la historia para crear las descripciones')
@click.option('--dir', '-d', type=str, default='historias_para_video', help='Ruta del directorio de las historias para crear las descripciones')
def main(file, dir):
    os.makedirs('.tmp/descripciones', exist_ok=True)
    if file:
        try:
            create_description(file)
        except Exception as e:
            print(f"Error creando descripciones para {file}: {e}. Exiting...")
            traceback.print_exc()
            return
    else:
        for file in os.listdir(dir):
            print("*" * 50)
            print(f"Creando descripciones para {file}")
            try:
                create_description(os.path.join(dir, file))
            except Exception as e:
                print(f"Error creando descripciones para {file}: {e}. Skipping...")
                traceback.print_exc()
                continue

def merge_oraciones(oraciones: list[str]):
    if len(oraciones) == 1:
        return oraciones
    merged_oraciones = []
    for i in range(len(oraciones)):
        words = oraciones[i].split()
        if len(words) <= 10:
            if i == len(oraciones) - 1:
                merged_oraciones[-1] += '. ' + oraciones[i]
            else:
                oraciones[i+1] = oraciones[i] + '. ' + oraciones[i+1]
        else:
            merged_oraciones.append(oraciones[i])
    return merged_oraciones if len(merged_oraciones) == len(oraciones) else merge_oraciones(merged_oraciones)


def create_description(file: str):
    with open(file, 'r') as f:
        historia = f.read()
    oraciones = [oracion.strip() for oracion in historia.split('.') if oracion.strip().replace('\n', '') != '']
    merged_oraciones = merge_oraciones(oraciones)

    story_sections = [section_list.join('. ') for section_list in merged_oraciones[::100]]
    
    titulo = file.split('/')[-1].split('.')[0].split('#')[0].strip()
    description_dir = f".tmp/descripciones/{titulo}"

    print("Creando descripciones...")
    descripciones = []
    for section in story_sections:
        for oracion in merged_oraciones:
            descripcion = get_description(section, oracion)
            if descripcion is not None:
                descripciones.append(descripcion)
                descripcion_anterior = descripcion
            else:
                descripciones.append(descripcion_anterior)
    
    pickle.dump(descripciones, open(f"{description_dir}.pkl", 'wb'))



def get_description(historia: str, oracion: str):
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
            return prompt
        except Exception as e:
            print(f"Error creating description: {e}. Retrying...")
            traceback.print_exc()
            retry_count += 1
            backoff_time = math.pow(2, retry_count)  # exponential backoff
            time.sleep(backoff_time)  # pause execution for backoff_time seconds

    if retry_count == max_retries:
        print("Max retries reached trying to create description. Exiting...")
        return None

if __name__ == '__main__':
    main()