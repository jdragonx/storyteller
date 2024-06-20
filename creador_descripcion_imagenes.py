#!/usr/bin/env python3
import pickle
import re
from openai import OpenAI
import click
import os
import traceback

max_retries = 5
client = OpenAI()
voices = {
    'terror': 'onyx',
    'cuentos': 'echo',
}

default_voice = voices[os.getcwd().split('/')[-1]]

@click.command()
@click.option('--file', '-f', type=str, help='Ruta del archivo de la historia para crear las descripciones')
@click.option('--dir', '-d', type=str, default='historias', help='Ruta del directorio de las historias para crear las descripciones')
@click.option('--output', '-o', type=str, default='.tmp/descripciones_imagenes', help='Ruta del directorio donde se guardarán las descripciones')
def main(file, dir, output):
    os.makedirs(output, exist_ok=True)
    if file:
        try:
            create_description(file, output)
        except Exception as e:
            print(f"Error creando descripciones para {file}: {e}. Exiting...")
            traceback.print_exc()
            return
    else:
        for file in os.listdir(dir):
            print("*" * 50)
            print(f"Creando descripciones para {file}")
            try:
                create_description(os.path.join(dir, file), output)
                # Luego movemos el archivo a la carpeta de historias para video
                os.rename(os.path.join(dir, file), os.path.join('historias_para_video', file))
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


def create_description(file: str, output: str):
    with open(file, 'r') as f:
        historia = f.read()
    oraciones = [oracion.strip() for oracion in historia.split('.') if oracion.strip().replace('\n', '') != '']
    merged_oraciones = merge_oraciones(oraciones)
    secciones_oraciones_lista = [merged_oraciones[i:i+25] for i in range(0, len(merged_oraciones), 25)]
    
    titulo = file.split('/')[-1].split('.')[0].split('#')[0].strip()
    titulo = re.sub(r'[:",;\'`´’‘“”«»(){}\[\]¡!¿?\\/áéíóúÁÉÍÓÚñÑàèìòùäëïöüçãõâêîôû]', '', titulo)
    description_dir = f"{output}/{titulo}"

    print("Creando descripciones...")
    descripciones = []
    descripcion_anterior = ''
    for (i, seccion_oraciones) in enumerate(secciones_oraciones_lista):
        print(f'Section {i+1} of {len(secciones_oraciones_lista)}')
        seccion = '. '.join(seccion_oraciones)
        for oracion in seccion_oraciones:
            descripcion = get_description(seccion, oracion)
            if descripcion is not None:
                descripciones.append(descripcion)
                descripcion_anterior = descripcion
            else:
                descripciones.append(descripcion_anterior)
    
    pickle.dump(descripciones, open(f"{description_dir}.pkl", 'wb'))



def get_description(historia: str, oracion: str):
    messages = [
        {'role': 'system', 'content': 'You are an assistant that receives a story, and a sentence extracted from it. With that you create a complete description of an image that will be used as a representation of the extracted sentence on a book. You make that image description convey the entire meaning of that extracted sentence according to the full context of the story, but keep the description short and concise. All the context and information should be contained on the image description. You always use english on the description.'},
        {'role': 'user', 'content': '{"story": "' + historia + '", "extracted_paragraph": "' + oracion + '"'},
    ]
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                max_tokens=100,
            )
            prompt = response.choices[0].message.content
            return prompt
        except Exception as e:
            print(f"Error creating description: {e}. Retrying...")
            traceback.print_exc()
            retry_count += 1

    return None

if __name__ == '__main__':
    main()