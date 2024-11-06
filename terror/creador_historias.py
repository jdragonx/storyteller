#!/usr/bin/env python3
import re
import traceback
from openai import OpenAI
import json
import random
import click
import os
import numpy as np
import datetime
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

client = OpenAI()

choices_final = [' El final debe ser terrorífico lleno de miedo e intriga de las cosas aterradoras que existen ahí fuera, nunca relatas un final ambiguo o bueno, solo finales escalofriantes.', 
        '']
probabilities = [0.6, 0.4]  # probabilities for each choice
tipo_de_final = np.random.choice(choices_final, p=probabilities)

persona_narracion = ['primera persona, de parte de un hombre', 'tercera persona, como narrador externo']
probabilities = [0.5, 0.5]  # probabilities for each choice
persona_narracion = np.random.choice(persona_narracion, p=probabilities)

estilo = "" if random.randint(0, 1) else " Siempre usas un estilo lovecraftiano en tus historias."

tipo_de_historia = "\n\n\nDebes tener en cuenta que la historia sea totalmente escalofriante, con sucesos inesperados y originales, dejando de lado los clásicos clichés y temáticas del terror, y usando nombres completamente inventados para los personajes que no evoquen a otras historias o peliculas. Añade diálogos cuando creas necesario. SIEMPRE EVITAS ESCRIBIR FRASES Y ORACIONES REDUNDANTES."

instrucciones_de_historia_final = ' Ten en cuenta que esta es la historia final, así que siempre evitas usar frases descriptivas como "el protagonista", "la historia termina con...", "dejando al lector...", etc., ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final.'

instrucciones_generales = ' Siempre evitas cometer errores ortográficos o gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta, y siempre en idioma español sin errores de codificación. Tus historias siempre están escritas en tiempo pasado, escribes con el estilo de un estudiante de colegio. Siempre respondes en formato json, el cual es un formato perfecto y puede ser parseado directamente en python.'

@click.command()
@click.option('--num_stories', '-n', default=1, type=int, help='Número de historias a crear')
@click.option('--short', '-s', is_flag=True, help='Crea historias cortas')
@click.option('--do_trends', '-t', is_flag=True, help='Crea historias basadas en tendencias')
def main(num_stories, short, do_trends):
    # Creación de las historias
    for i in range(num_stories):
        print(f"Creando historia {i+1} de {num_stories}")
        create_story(short, do_trends)
        print(f"*" * 50)

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
        'portal dimensional',
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
        'amorío',
        'videojuego',
        'enfermo mental',
        'párroco',
        'religión',
        'tema_removido',
        'tema_removido',
        'tema_removido',
        'tema_removido',
        'tema_removido',
        'tema_removido',
        'vacunas',
        'cuevas',
        'free fire',
        'guerra',
        'psicópata',
        'manipulación',
        'trampas letales',
        'juegos mortales',
        'criaturas acuaticas',
        'lago',
        'oceano',
        'gemelos'
    ]

    n_details = 1 if do_trends else random.choices([0, 1], weights=[4, 1])[0]
    details: list = random.sample(details, n_details)

    details_instructions = f", siempre te aseguras de poner todos los siguientes detalles en el outline: {', '.join(details).lower()}" if len(details) else ""
    format_instructions = '{"outline": "aquí pones el outline, de forma seguida y continua, sin bullet points ni numeración.", "titulo": "aquí pondrás el título de la historia, debes tener en cuenta que debe ser un título muy intrigante, el cual llame la atención enseguida con solo verlo y obligue a las personas abrir la historia para saber de qué se trata. La historia será publicada online por lo que el título es extremadamente importante, piensa que será narrada en un video de youtube, por eso el título debe ser el que daría los mejores resultados para que los usuarios de youtube que lo vean den click en el video. Además debe ser un título corto, máximo de 7 palabras. El título siempre debe ser en idioma español, sin errores de codificación."}'

    longitud = " La historia va a ser leída con una duración de 1 hora y tendrá 10.000 palabras, con varios párrafos. Expande cada tema del outline en su totalidad y con extremo detalle." if not short else " La historia va a ser leída con una duración de 1 minuto y medio y tendrá alrededor de 300 palabras, con un único párrafo."

    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea un outline para una historia de terror{details_instructions}.{longitud}{tipo_de_historia}{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_generales} Siempre envías el formato json correcto, el cual sigue estas directrices: {format_instructions}'},
    ]
    
    retry = 0
    while (retry < 5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                seed=datetime.datetime.now().timestamp().__int__()
            )
            parsed_response = json.loads(response.choices[0].message.content)
            titulo_original: str = parsed_response['titulo']
            outline = parsed_response['outline']
            break
        except Exception as e:
            print(f"Error creating chat completion: {e}")
            traceback.print_exc()
            retry += 1

    if not titulo_original or not outline:
        print("No se pudo crear el outline")
        return

    # Creación de la historia a partir del outline
    print("Creando historia...")
    format_instructions_historia = '{"historia": "Aquí pones la historia.", "titulos_posibles": ["Aquí pondrás 10 posibles nuevos títulos de la historia en un formato de lista para python. Dado que ya has terminado de escribir la historia debes escoger mejores títulos para ella. El título debe ser único y completamente original. Recuerda que debe ser un título muy intrigante, el cual llame la atención enseguida con solo verlo y obligue a las personas abrir la historia para saber de qué se trata. La historia será publicada online por lo que el título es extremadamente importante, piensa que será narrada en un video de youtube, por eso el título debe ser el que daría los mejores resultados para que los usuarios de youtube que lo vean den click en el video. Además debe ser un título corto, máximo de 7 palabras. El título siempre debe ser en idioma español, sin errores de codificación."]}'
    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea una historia de terror a partir de un outline y un título.{longitud} El título de la historia es "{titulo_original}", y el outline es el siguiente: "{outline}".{tipo_de_historia}{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final} La historia siempre debe tener un final.{instrucciones_de_historia_final}{instrucciones_generales} Siempre envías el formato json correcto, el cual sigue estas directrices: {format_instructions_historia}'},
    ]

    retry = 0
    historia = None
    while (retry < 5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0,
                seed=7
            )
            parsed_response = json.loads(response.choices[0].message.content)
            historia = parsed_response['historia']
            titulos_posibles: list[str] = parsed_response['titulos_posibles']
            break
        except Exception as e:
            print(f"Error creating chat completion: {e}")
            traceback.print_exc()
            retry += 1
    
    if historia is None:
        print("No se pudo crear la historia")
        return
    
    # Either increase the length of the story if it's too short, or reduce it if it's too long, depending on the 'short' parameter
    current_attempt = 0
    if not short:
        while historia and (len(re.findall(r'\b\w+\b', historia)) < 1000) and current_attempt < 10:
            historia = increase_length(historia)
            current_attempt += 1
        if current_attempt >= 10:
            print("No se pudo expandir la historia")
            return
    else:
        while historia and (len(re.findall(r'\b\w+\b', historia)) > 350) and current_attempt < 10:
            historia = reduce_length(historia)
            current_attempt += 1
        if current_attempt >= 10:
            print("No se pudo reducir la historia")
            return
    
    descripcion = crear_descripcion_historia(historia)
    # Remove the dot on abreviations like Mr., Sr., Ms., Mrs., etc. and convert '...' to '.'
    historia = re.sub(r'\b(Mr|Sr|Ms|Mrs|Dr|St|Jr)\.', r'\1', historia)
    historia = re.sub(r'\.\.\.', r'.', historia)

    # Remove ':' from the title, and replace it with ','
    titulo = titulo_original.replace(':', ',').title()

    # Define the base file name
    base_filename = f'./historias/'
    base_filename_video = f'./historias_para_video/'
    base_filename_terminadas = f'./historias_terminadas/'
    base_filename_ya_subidas = f'./historias_ya_subidas/'

    # Define the hashtag part
    hashtag_part = ' #terror #miedo.txt'

    # Check if the file already exists in any of the directories
    suffix = ""
    while (
            os.path.isfile(f'{base_filename}{titulo}{suffix}{hashtag_part}')
            or os.path.isfile(f'{base_filename_video}{titulo}{suffix}{hashtag_part}')
            or os.path.isfile(f'{base_filename_terminadas}{titulo}{suffix}{hashtag_part}')
            or os.path.isfile(f'{base_filename_ya_subidas}{titulo}{suffix}{hashtag_part}')
        ):
        # If it does first let's see if we can remove articles from the title
        if titulo.lower().startswith("la "):
            titulo = titulo[3:].title()
        elif titulo.lower().startswith("el "):
            titulo = titulo[3:].title()
        elif titulo.lower().startswith("los "):
            titulo = titulo[4:].title()
        elif titulo.lower().startswith("las "):
            titulo = titulo[4:].title()
        else:
            # Then we try to see if the titles from the list of possible titles are available and if they work
            try:
                titulo = titulos_posibles.pop(0).replace(':', ',').title()
            except IndexError:
                # If there are no more titles, we try to append a suffix to the title
                suffix += " II"
    else:
        # We found a filename that doesn't exist, let's create the file
        filename = f'{base_filename}{titulo}{suffix}{hashtag_part}'

    # Write the story to the file
    with open(filename, 'w') as f:
        print(f"Guardando historia: {titulo}")
        f.write(historia)
    
    # Write the description to the file
    descripcion_filename = f'./descripciones_historias/{filename.split("/")[-1]}'
    with open(descripcion_filename, 'w') as f:
        f.write(descripcion)

def increase_length(historia: str):
    # Extension de la historia
    print("Extendiendo historia...")
    format_instructions_historia_larga = '{"historia_expandida": "aquí pones la historia expandida, recuerda que debe ser mucho más extensa que la original, la nueva historia debe ser al menos 10 veces más extensa que la original, si no cumples con la longitud esperada se te pedirá que vuelvas a expandir la historia resultante hasta lograr la longitud esperada de entre 2000 y 6000 palabras, con varios párrafos."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia pequeña e instantáneamente la transformas en un hit que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias pequeñas sean expandidas en historias grandes, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras con paciencia para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real. Siempre expandes cada oración de la historia, sin dejar ninguna oración sin haber sido expandida, para poder construir así una atmósfera completamente envolvente.{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_de_historia_final}{instrucciones_generales} Usas varios párrafos para dar mayor facilidad a la lectura de tus historias. El formato json de tu respuesta es el siguiente: {format_instructions_historia_larga}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]

    retry = 0
    while (retry < 5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0,
                seed=7
            )
            parsed_response = json.loads(response.choices[0].message.content)
            historia_expandida = parsed_response['historia_expandida']
            return historia_expandida
        except Exception as e:
            print(f"Error creating chat completion: {e}")
            traceback.print_exc()
            retry += 1
    return historia

def reduce_length(historia: str):
    # Reducción de la historia
    print("Reduciendo historia...")
    format_instructions_historia_corta = '{"historia_reducida": "aquí pones la historia reducida, recuerda que debe ser más corta que la original, debe tener alrededor de 300 palabras, con un único párrafo."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia grande e instantáneamente la transformas en una historia pequeña que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias grandes sean reducidas en historias un poco más pequeñas, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real.{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_de_historia_final}{instrucciones_generales} Usas un único párrafo para dar mayor facilidad a la lectura de tus historias. El formato json de tu respuesta es el siguiente: {format_instructions_historia_corta}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]

    retry = 0
    while (retry < 5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0,
                seed=7
            )
            parsed_response = json.loads(response.choices[0].message.content)
            historia_reducida = parsed_response['historia_reducida']
            return historia_reducida
        except Exception as e:
            print(f"Error creating chat completion: {e}")
            traceback.print_exc()
            retry += 1
    return historia

def crear_descripcion_historia(historia: str):
    # Truncar la historia a 11000 tokens para evitar errores
    historia = encoder.decode(encoder.encode(historia)[:11000])
    # Creación de la descripción de la historia
    print("Creando descripción de la historia...")
    format_instructions_descripcion = '{"descripcion": "aquí pones la descripción de la historia, debe ser un resumen de la historia, que contenga la esencia de la historia, sin revelar el final, y que sea lo suficientemente intrigante para que el lector quiera leer la historia completa. Puedes usar emojis para la descripción. Recuerda que la descripción debe ser en español, sin errores de codificación. La descripción debe ser corta, de máximo 100 palabras, con un único párrafo."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia y creas una descripción que la acompañe. Para lograr eso siempre te enfocas en que las descripciones conversen su esencia, no cambias el tipo de historia. Creas descripciones que sean un resumen de la historia, que contengan la esencia de la historia, sin revelar el final, y que sean lo suficientemente intrigantes para que el lector quiera leer la historia completa.{estilo} Siempre narras tus historias en {persona_narracion}.{instrucciones_generales}. El formato json de tu respuesta es el siguiente: {format_instructions_descripcion}\n\n\n\nLa historia es la siguiente:\n\n\n\n"{historia}"'},
    ]

    retry = 0
    while (retry < 5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0,
                seed=7
            )
            parsed_response = json.loads(response.choices[0].message.content)
            return parsed_response['descripcion']
        except Exception as e:
            print(f"Error creating chat completion: {e}")
            retry += 1

    return ""

if __name__ == '__main__':
    main()