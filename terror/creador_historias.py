#!/usr/bin/env python3
import re
from openai import OpenAI
import json
import random
import click
import ast
import os
import numpy as np
import datetime

client = OpenAI()

choices = [' El final debe ser terrorífico lleno de miedo e intriga de las cosas aterradoras que existen ahí fuera, nunca relatas un final ambiguo o bueno, solo finales escalofriantes.', 
        '']
probabilities = [0.6, 0.4]  # probabilities for each choice
tipo_de_final = np.random.choice(choices, p=probabilities)

persona_narracion = ['primera persona, de parte de un hombre', 'tercera persona']
probabilities = [0.5, 0.5]  # probabilities for each choice
persona_narracion = np.random.choice(persona_narracion, p=probabilities)

@click.command()
@click.option('--num_stories', '-n', default=1, type=int, help='Número de historias a crear')
@click.option('--short', '-s', is_flag=True, help='Crea historias cortas')
@click.option('--do_trends', '-t', is_flag=True, help='Crea historias basadas en tendencias')
def main(num_stories, short, do_trends):
    
    for i in range(num_stories):
        print(f"Creando historia {i+1} de {num_stories}")
        create_story(short, do_trends)

def create_story(short: bool, do_trends: bool):
    # Creación del outline
    print("Creando outline...")
    details = [
        'cientificos',
        'ouija',
        'zombies',
        'animales asesinos',
        'crucero',
        'san valentin',
        'navidad',
        'cementerio',
        'fantasmas vengativos',
        'vampiros',
        'demonios',
        'marionetas',
        'hombres lobo',
        'ciudad',
        'asesino serial',
        'venganza',
        'canibalismo',
        'payasos',
        'pesadillas',
        'experimentos geneticos',
        'juegos de mesa malditos',
        'orfanato abandonado',
        'bosque encantado',
        'mansiones embrujadas',
        'maldiciones familiares',
        'artefactos poseidos',
        'niebla misteriosa',
        'brujeria ancestral',
        'viajes en el tiempo terrorificos',
        'locura colectiva',
        'islas desiertas',
        'espejos encantados',
        'enfermedades sobrenaturales',
        'apocalipsis tecnologico',
        'carnaval siniestro',
        'libros encantados',
        'viajes espaciales aterradores',
        'refugios subterraneos',
        'circo maldito',
        'invasión extraterrestre',
        'cárcel abandonada',
        'posesiones demoníacas',
        'viaje interdimensional',
        'fenómenos paranormales en hospitales',
        'culto oscuro',
        'pueblo fantasma',
        'científicos locos',
        'manicomio embrujado',
        'profecías macabras',
        'brujas urbanas',
        'reliquias malditas',
        'criaturas acuáticas',
        'meteorito alienígena',
        'feria embrujada',
        'fábrica abandonada',
        'infiltración en secta',
        'asesinos de leyendas urbanas',
        'robots asesinos',
        'casa de muñecas poseída',
        'máquinas poseídas',
        'gárgolas vivientes',
        'pantanos tenebrosos',
        'cámaras de vigilancia espeluznantes',
        'tecnología paranormal',
        'posesión de objetos cotidianos',
        'rituales en desiertos',
        'caza de brujas moderna',
        'misterios en la deep web',
        'túneles subterráneos misteriosos',
        'neblina mortal',
        'escuela encantada',
        'artefactos alienígenas',
        'coleccionistas macabros',
        'experimentos secretos del gobierno',
        'sociedad secreta',
        'accidentes espeluznantes en parques de atracciones',
        'ferrocarriles malditos',
        'cosechas terroríficas',
        'laboratorio genético oculto',
        'carreteras desiertas',
        'pandemia',
        'prisión espectral',
        'tecnología fantasma',
        'criaturas de la cripta',
        'mercado negro paranormal',
        'búnkeres poseídos',
        'robots con inteligencia artificial malévola',
        'juegos diabólicos',
        'juguetes siniestros',
        'videojuegos',
        'broma que sale mal',
    ]

    trends = [
        'amorío',
        'videojuego',
        'enfermo mental',
        'párroco',
        'religión',
        'tema_removido',
        'niño obeso',
        'tema_removido',
        'tema_removido',
        'eutanasia',
        'pena de muerte',
        'tema_removido',
        'tema_removido',
        'feminista',
        'gay',
        'transexual',
        'tema_removido',
    ]

    n_details = 1 if do_trends else random.randint(0, 1)
    details: list = random.sample(trends if do_trends else details, n_details)

    details_instructions = f", siempre te aseguras de poner todos los siguientes detalles en el outline: {', '.join(details).lower()}" if len(details) else ""
    format_instructions = '{"outline": "aquí pones el outline, de forma seguida y continua, sin bullet points ni numeración.", "titulo": "aquí pondrás el título de la historia, debes tener en cuenta que debe ser un título muy intrigante, el cual llame la atención enseguida con solo verlo y obligue a las personas abrir la historia para saber de qué se trata. La historia será publicada online por lo que el título es extremadamente importante, piensa que será narrada en un video de youtube, por eso el título debe ser el que daría los mejores resultados para que los usuarios de youtube que lo vean den click en el video. Además debe ser un título corto, máximo de 7 palabras."}'

    longitud = " La historia va a ser leída con una duración de entre 10 a 15 minutos y tendrá entre 1000 y 3000 palabras, con varios párrafos." if not short else " La historia va a ser leída con una duración de 30 segundos y tendrá alrededor de 100 palabras, con un único párrafo."

    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea un outline para una historia de terror{details_instructions}.{longitud}\n\nDebes tener en cuenta que la historia sea totalmente escalofriante, con sucesos inesperados y originales, dejando de lado los clásicos clichés y temáticas del terror, y usando nombres completamente inventados para los personajes que no evoquen a otras historias o peliculas. Añade diálogos cuando creas necesario. NUNCA ESCRIBES FRASES NI ORACIONES REDUNDANTES. Siempre narras tus historias en {persona_narracion}.{tipo_de_final} Siempre evitas cometer errores ortográficos o gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta. Tus historias siempre están escritas en tiempo pasado, escribes con el estilo de un estudiante de colegio. Tu respuesta es en formato json, usas el siguiente formato, este formato será utilizado en python y parseado automáticamente. Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions}'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            response_format={"type": "json_object"},
            seed=datetime.datetime.now().timestamp().__int__()
        )
        parsed_response = json.loads(response.choices[0].message.content)
        titulo = parsed_response['titulo']
        outline = parsed_response['outline']
    except Exception as e:
        print(f"Error creating chat completion: {e}")
        return

    parsed_response = json.loads(response.choices[0].message.content)
    titulo = parsed_response['titulo']
    outline = parsed_response['outline']

    # Creación de la historia a partir del outline
    print("Creando historia...")
    format_instructions_historia = '{"titulo": "aquí pondrás el título de la historia", "historia": "Aquí pones la historia."}'
    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea una historia de terror a partir de un outline y un título.{longitud} Expande cada tema del outline en su totalidad y con extremo detalle. El título de la historia es "{titulo}", y el outline es el siguiente: "{outline}".\n\n\nDebes tener en cuenta que la historia sea totalmente escalofriante, con sucesos inesperados y originales, dejando de lado los clásicos clichés y temáticas del terror, y usando nombres completamente inventados para los personajes que no evoquen a otras historias o peliculas. Añade diálogos cuando creas necesario. SIEMPRE EVITAS ESCRIBIR FRASES Y ORACIONES REDUNDANTES. Siempre narras tus historias en {persona_narracion}.{tipo_de_final} Ten en cuenta que esta es la historia final, así que siempre evitas usar frases descriptivas como "el protagonista", "la historia termina con...", "dejando al lector...", etc., ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final. Siempre evitas cometer errores ortográficos o gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta, y siempre en idioma español sin errores de codificación. Tus historias siempre están escritas en tiempo pasado, escribes con el estilo de un estudiante de colegio. Tu respuesta es en formato json, usas el siguiente formato, este formato será utilizado en python y parseado automáticamente. Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions_historia}'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0,
            seed=datetime.datetime.now().timestamp().__int__()
        )
        parsed_response = json.loads(response.choices[0].message.content)
        historia = parsed_response['historia']
    except Exception as e:
        print(f"Error creating chat completion: {e}")
        return
    
    # Either increase the length of the story if it's too short, or reduce it if it's too long, depending on the 'short' parameter
    current_attempt = 0
    while historia and (len(re.findall(r'\b\w+\b', historia)) < 500) and not short and current_attempt < 10:
        historia = increase_length(historia)
        current_attempt += 1
    
    while historia and (len(re.findall(r'\b\w+\b', historia)) > 110) and short and current_attempt < 10:
        historia = reduce_length(historia)
        current_attempt += 1

    # Define the base file name
    base_filename = f'./historias/{titulo} #terror #miedo.txt'
    base_filename_video = f'./historias_para_video/{titulo} #terror #miedo.txt'
    base_filename_terminadas = f'./historias_terminadas/{titulo} #terror #miedo.txt'
    base_filename_ya_subidas = f'./historias_ya_subidas/{titulo} #terror #miedo.txt'

    # Check if the file already exists in any of the directories
    if (
            os.path.isfile(base_filename)
            or os.path.isfile(base_filename_video)
            or os.path.isfile(base_filename_terminadas)
            or os.path.isfile(base_filename_ya_subidas)
        ):
        # If it does, append a 'II' to the title
        filename = f'./historias/{titulo} II #terror #miedo.txt'
    else:
        # If it doesn't, use the base file name
        filename = base_filename

    # Write the story to the file
    with open(filename, 'w') as f:
        f.write(historia)

def increase_length(historia: str):
    # Extension de la historia
    print("Extendiendo historia...")
    format_instructions_historia_larga = '{"historia_expandida": "aquí pones la historia expandida, recuerda que debe ser mucho más extensa que la original, la nueva historia debe ser al menos 10 veces más extensa que la original"}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia pequeña e instantáneamente la transformas en un hit que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias pequeñas sean expandidas en historias grandes, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras con paciencia para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real. Siempre expandes cada oración de la historia, sin dejar ninguna oración sin haber sido expandida, para poder construir así una atmósfera completamente envolvente. Siempre narras tus historias en {persona_narracion}.{tipo_de_final} Ten en cuenta que esta es la historia final, así que siempre evitas usar frases descriptivas como "el protagonista", "la historia termina con...", "dejando al lector...", etc., ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final. Siempre evitas cometer errores ortográficos o gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta, y siempre en idioma español sin errores de codificación. Tus historias siempre están escritas en tiempo pasado, escribes con el estilo de un estudiante de colegio. Siempre respondes en formato json, el cual es un formato perfecto y puede ser parseado directamente en python. Usas varios párrafos para dar mayor facilidad a la lectura de tus historias. El formato de tu respuesta es el siguiente: {format_instructions_historia_larga}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0,
            seed=datetime.datetime.now().timestamp().__int__()
        )
        parsed_response = json.loads(response.choices[0].message.content)
        historia_expandida = parsed_response['historia_expandida']
        return historia_expandida
    except Exception as e:
        print(f"Error creating chat completion: {e}")
        return historia

def reduce_length(historia: str):
    # Reducción de la historia
    print("Reduciendo historia...")
    format_instructions_historia_corta = '{"historia_reducida": "aquí pones la historia reducida, recuerda que debe ser más corta que la original, debe tener alrededor de 100 palabras, con un único párrafo."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia grande e instantáneamente la transformas en una historia pequeña que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias grandes sean reducidas en historias pequeñas, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real. Siempre narras tus historias en {persona_narracion}.{tipo_de_final} Ten en cuenta que esta es la historia final, así que siempre evitas usar frases descriptivas como "el protagonista", "la historia termina con...", "dejando al lector...", etc., ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final. Siempre evitas cometer errores ortográficos o gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta, y siempre en idioma español sin errores de codificación. Tus historias siempre están escritas en tiempo pasado, escribes con el estilo de un estudiante de colegio. Siempre respondes en formato json, el cual es un formato perfecto y puede ser parseado directamente en python. Usas un único párrafo para dar mayor facilidad a la lectura de tus historias. El formato de tu respuesta es el siguiente: {format_instructions_historia_corta}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0,
            seed=datetime.datetime.now().timestamp().__int__()
        )
        parsed_response = json.loads(response.choices[0].message.content)
        historia_reducida = parsed_response['historia_reducida']
        return historia_reducida
    except Exception as e:
        print(f"Error creating chat completion: {e}")
        return historia

if __name__ == '__main__':
    main()