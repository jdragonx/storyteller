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
import difflib

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
@click.option('--long', '-l', is_flag=True, help='Crea historias largas usando la historia corta o normal como base')
def main(num_stories, short, do_trends, long):
    # Creación de las historias
    for i in range(num_stories):
        print(f"Creando historia {i+1} de {num_stories}")
        create_story(short, do_trends, long)

def create_story(short: bool, do_trends: bool, long: bool):
    # Historias largas definimos l final siempre en nuestro final personalizado, ya que al extender la historia, el final puede cambiar.
    # así nos aseguramos de que el final sea el personalizado una mayor cantidad de veces.
    global tipo_de_final
    if long:
        tipo_de_final = choices_final[0]
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

    trends = [
        'mr beast'
    ]

    n_details = 1 if do_trends else random.choices([0, 1], weights=[4, 1])[0]
    details: list = random.sample(trends if do_trends else details, n_details)

    details_instructions = f", siempre te aseguras de poner todos los siguientes detalles en el outline: {', '.join(details).lower()}" if len(details) else ""
    format_instructions = '{"outline": "aquí pones el outline, de forma seguida y continua, sin bullet points ni numeración.", "titulo": "aquí pondrás el título de la historia, debes tener en cuenta que debe ser un título muy intrigante, el cual llame la atención enseguida con solo verlo y obligue a las personas abrir la historia para saber de qué se trata. La historia será publicada online por lo que el título es extremadamente importante, piensa que será narrada en un video de youtube, por eso el título debe ser el que daría los mejores resultados para que los usuarios de youtube que lo vean den click en el video. Además debe ser un título corto, máximo de 7 palabras. El título siempre debe ser en idioma español, sin errores de codificación."}'

    longitud = " La historia va a ser leída con una duración de entre 10 a 15 minutos y tendrá entre 1000 y 3000 palabras, con varios párrafos. Expande cada tema del outline en su totalidad y con extremo detalle." if not short else " La historia va a ser leída con una duración de 30 segundos y tendrá alrededor de 100 palabras, con un único párrafo."

    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea un outline para una historia de terror{details_instructions}.{longitud}{tipo_de_historia}{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_generales} Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions}'},
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

    # Creación de la historia a partir del outline
    print("Creando historia...")
    format_instructions_historia = '{"titulo": "aquí pondrás el título de la historia", "historia": "Aquí pones la historia."}'
    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea una historia de terror a partir de un outline y un título.{longitud} El título de la historia es "{titulo}", y el outline es el siguiente: "{outline}".{tipo_de_historia}{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final} La historia siempre debe tener un final.{instrucciones_de_historia_final}{instrucciones_generales} Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions_historia}'},
    ]
    
    try:
        response = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            model="gpt-3.5-turbo-0125",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0,
            seed=7
        )
        parsed_response = json.loads(response.choices[0].message.content)
        historia = parsed_response['historia']
    except Exception as e:
        print(f"Error creating chat completion: {e}")
        return
    
    # Either increase the length of the story if it's too short, or reduce it if it's too long, depending on the 'short' parameter
    # If 'long' is set, create a really long story
    current_attempt = 0
    if long:
        historia = create_really_long(historia)
    elif not short:
        while historia and (len(re.findall(r'\b\w+\b', historia)) < 500) and current_attempt < 10:
            historia = increase_length(historia)
            current_attempt += 1
    else:
        while historia and (len(re.findall(r'\b\w+\b', historia)) > 110) and current_attempt < 10:
            historia = reduce_length(historia)
            current_attempt += 1
    # Remove the dot on abreviations like Mr., Sr., Ms., Mrs., etc. and convert '...' to '.'
    historia = re.sub(r'\b(Mr|Sr|Ms|Mrs|Dr|St|Jr)\.', r'\1', historia)
    historia = re.sub(r'\.\.\.', r'.', historia)    

    # Define the base file name
    base_filename = f'./historias/{titulo} #terror #miedo.txt'
    base_filename_video = f'./historias_para_video/{titulo} #terror #miedo.txt'
    base_filename_terminadas = f'./historias_terminadas/{titulo} #terror #miedo.txt'
    base_filename_ya_subidas = f'./historias_ya_subidas/{titulo} #terror #miedo.txt'

    # Check if the file already exists in any of the directories
    suffix = ""
    while (
            os.path.isfile(f'{base_filename}{suffix}')
            or os.path.isfile(f'{base_filename_video}{suffix}')
            or os.path.isfile(f'{base_filename_terminadas}{suffix}')
            or os.path.isfile(f'{base_filename_ya_subidas}{suffix}')
        ):
        # If it does, append a 'II' to the title then check again
        suffix += " II"
        filename = f'./historias/{titulo} {suffix} #terror #miedo.txt'
        base_filename_video = f'./historias_para_video/{titulo} {suffix} #terror #miedo.txt'
        base_filename_terminadas = f'./historias_terminadas/{titulo} {suffix} #terror #miedo.txt'
        base_filename_ya_subidas = f'./historias_ya_subidas/{titulo} {suffix} #terror #miedo.txt'
        base_filename = f'./historias/{titulo} {suffix} #terror #miedo.txt'
    else:
        # If it doesn't, use the base file name
        filename = base_filename

    # Write the story to the file
    with open(filename, 'w') as f:
        f.write(historia)

def increase_length(historia: str):
    # Extension de la historia
    print("Extendiendo historia...")
    format_instructions_historia_larga = '{"historia_expandida": "aquí pones la historia expandida, recuerda que debe ser mucho más extensa que la original, la nueva historia debe ser al menos 10 veces más extensa que la original, si no cumples con la longitud esperada se te pedirá que vuelvas a expandir la historia resultante hasta lograr la longitud esperada de entre 1000 y 3000 palabras, con varios párrafos."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia pequeña e instantáneamente la transformas en un hit que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias pequeñas sean expandidas en historias grandes, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras con paciencia para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real. Siempre expandes cada oración de la historia, sin dejar ninguna oración sin haber sido expandida, para poder construir así una atmósfera completamente envolvente.{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_de_historia_final}{instrucciones_generales} Usas varios párrafos para dar mayor facilidad a la lectura de tus historias. El formato de tu respuesta es el siguiente: {format_instructions_historia_larga}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]
    
    try:
        response = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            model="gpt-3.5-turbo-0125",
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
        return historia

def reduce_length(historia: str):
    # Reducción de la historia
    print("Reduciendo historia...")
    format_instructions_historia_corta = '{"historia_reducida": "aquí pones la historia reducida, recuerda que debe ser más corta que la original, debe tener alrededor de 100 palabras, con un único párrafo."}'
    messages = [
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia grande e instantáneamente la transformas en una historia pequeña que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias grandes sean reducidas en historias un poco más pequeñas, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real.{estilo} Siempre narras tus historias en {persona_narracion}.{tipo_de_final}{instrucciones_de_historia_final}{instrucciones_generales} Usas un único párrafo para dar mayor facilidad a la lectura de tus historias. El formato de tu respuesta es el siguiente: {format_instructions_historia_corta}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]

    try:
        response = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            model="gpt-3.5-turbo-0125",
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
        return historia

def create_really_long(historia: str, extension = 30):
    # Creación de una historia realmente larga
    print("Creando historia realmente larga...")
    libro: str = ""
    context_length_exceeded = False

    for i in range(extension + 2):
        print(f"Creando sección {i+1} de {extension}")
        libro_a_enviar = '.'.join(libro.split('.')[-20:]) + "." if context_length_exceeded else libro
        instruccion_final = ' Esta es la última sección así que debes darle el final en esta sección a lo que has ido construyendo' if (i>=(extension-1)) else ''

        format_instructions_historia_larga = '{"seccion": Esta es la sección del libro en la que te encuentras ahora, "contenido_seccion": "aquí escribes el contenido de la sección del libro, recuerda que debes escribir el libro en '+str(extension)+' secciones. El libro será al menos '+str(extension)+' veces más extenso que la historia original, para ello cada sección debe tener entre 1000 y 3000 palabras, con varios párrafos."}'
        messages = [
        {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia pequeña y la transformas en un libro, el que es un hit que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias pequeñas sean expandidas en libros, pero conversen su esencia, no cambias nunca el tipo de historia, creas grandes escenarios y sucesos que narras con paciencia para lograr que la atmósfera atrape al lector y lo lleve al mundo del libro como si fuera real.{tipo_de_historia}{estilo} Siempre narras tus historias en {persona_narracion}.{instrucciones_de_historia_final}{instrucciones_generales} Para poder escribir la historia la haremos por partes, poco a poco en {extension} secciones. Para ello tienes acceso al libro completo de lo que has escrito hasta ahora, la historia pequeña original, y sabrás en cuál sección te encuentras en este momento. SIEMPRE EVITAS LA REPETICIÓN DE IDEAS Y LA REPETICIÓN DE PALABRAS Y FRASES, MANTENIENDO COHERENCIA Y FLUIDEZ EN TODA LA HISTORIA.{instruccion_final} El formato de tu respuesta es el siguiente: {format_instructions_historia_larga}\n\n\n\nLa historia pequeña es la siguiente:\n\n\n\n"{historia}".\n\n\n\nEl libro hasta ahora es el siguiente:\n\n\n\n"{libro_a_enviar}". Estás en la sección {i+1}.'},
        ]
        
        retry = 0
        while (retry < 5):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_tokens=4000,
                    temperature=0.5,
                    presence_penalty=0.5,
                    seed=datetime.datetime.now().timestamp().__int__()
                )
                parsed_response = json.loads(response.choices[0].message.content)
                contenido_seccion: str = parsed_response['contenido_seccion']

                # Revisamos si la seccion tiene repeticiones en su interior o con la seccion anterior
                repetitivo = verificar_textos_repetitivos(libro, contenido_seccion)
                if repetitivo:
                    print("Sección repetitiva, eliminando sección.")
                    contenido_seccion = ''
                libro += f" {contenido_seccion}" if i > 0 else contenido_seccion
                break
            except Exception as e:
                if hasattr(e, 'code') and e.code == 'context_length_exceeded':
                    context_length_exceeded = True
                print(f"Error creating chat completion: {e}")
                traceback.print_exc()
                retry += 1

    return re.sub(' +', ' ', libro)

def verificar_textos_repetitivos(texto1, texto2):
    # Dividir los textos en oraciones
    oraciones1 = texto1.split('.')
    oraciones2 = texto2.split('.')

    # Verificar si hay oraciones duplicadas dentro de cada texto
    if len(oraciones1) != len(set(oraciones1)) or len(oraciones2) != len(set(oraciones2)):
        return True
    
    # Verificar si alguno de los textos está vacío, en cuyo caso no se considera repetitivo
    if not texto1 or not texto2:
        return False

    # Determinar cuál texto es más largo
    if len(texto1) > len(texto2):
        texto1 = texto1[-len(texto2):]
    else:
        texto2 = texto2[-len(texto1):]

    # Dividir los nuevos textos en oraciones y ponerlos en un set
    oraciones1 = set(texto1.split('.'))
    oraciones2 = set(texto2.split('.'))

    # Comparar las oraciones y contar cuántas son iguales
    match = oraciones1.intersection(oraciones2)

    # Devolver True si hay al menos una oración idéntica, False en caso contrario
    return len(match) > 0

if __name__ == '__main__':
    main()