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

choices = [' El final debe ser uno donde las cosas salen muy mal por alguna razón, pero eso sirve para aprender la lección, nunca relatas un final ambiguo o bueno, solo finales desesperanzadores, con una dura lección por aprender.',
        ' El final debe ser bueno, con una resolución clara y positiva, dejando al lector con una sensación de alivio, felicidad y una lección aprendida para usar en la vida diaria. Ya sea que las decisiones fueron las correctas, la lección fue aprendida, la vida da otra oportunidad, o que las cosas salen bien por alguna razón, o con algún tipo de esperanza, siempre escribes finales positivos.']
probabilities = [0.5, 0.5]  # probabilities for each choice
tipo_de_final = np.random.choice(choices, p=probabilities)

@click.command()
@click.option('--num_stories', '-n', default=1, type=int, help='Número de historias a crear')
@click.option('--short', '-s', is_flag=True, help='Crea historias cortas')
def main(num_stories, short):
    
    for i in range(num_stories):
        print(f"Creando historia {i+1} de {num_stories}")
        create_story(short)

def create_story(short: bool):
    historias_existentes = os.listdir('./historias')
    historias_existentes.extend(os.listdir('./historias_para_video/'))
    historias_existentes.extend(os.listdir('./historias_terminadas/'))
    historias_existentes = [historia.replace(' | Cuento |  Relato |  Aventura | Superación.txt', '') for historia in historias_existentes]
    historias_existentes = list(set(historias_existentes))
    # Creación del outline
    print("Creando outline...")
    details = [
        'Resiliencia', 
        'Enfrenta desafíos',
        'Supera obstáculos',
        'Fuerza interior', 
        'Autoaceptación', 
        'Superando inseguridades', 
        'Relación positiva',
        'Perseverancia', 
        'Metas significativas',
        'Sacrificios', 
        'Desafíos determinación',
        'Transformación', 
        'Experimenta cambio',
        'Crecimiento mental', 
        'Desarrollo personal',
        'Aprendizaje', 
        'Fracasos adversidades', 
        'Empoderamiento liderazgo'
        'Descubre poder', 
        'Lidera cambios',
        'Influenciando motivando',
        'Perdón', 
        'Sanación emocional', 
        'Avanzar paz',
        'Cambio perspectiva',
        'Nueva oportunidad', 
        'Nuevos horizontes',
        'Solidaridad', 
        'Colaboración apoyo', 
        'Autodescubrimiento',
        'Búsqueda profunda', 
        'Significado vida',
        'Descubriendo pasiones', 
        'Realización personal',
        'Desafiando límites', 
        'Supera expectativas',
        'Rompimiento barreras', 
        'Alcanza sueños',
        'Perseguir pasiones', 
        'Construye propósito',
        'Vencer miedos', 
        'Encuentra valentía',
        'Fortaleza interior', 
        'Equilibrio emocional',
        'Descubrimiento interno', 
        'Aceptación personal',
        'Reconstruir sueños', 
        'Recuperar esperanza',
        'Explorando potencial', 
        'Desarrollo individual',
        'Reinventarse vida', 
        'Nuevos comienzos',
        'Descubriendo fortalezas', 
        'Superando debilidades',
        'Transformación radical', 
        'Renovación total',
        'Perspectivas renovadas', 
        'Enfoque renovado',
        'Resurgir adversidades', 
        'Triunfar adversidades',
        'Superar barreras', 
        'Conquista metas',
        'Navegando incertidumbre', 
        'Enfrentando cambios',
        'Aprendiendo caídas',
        'Inversiones',
        'Ahorro',
        'Administracion',
        'Finanzas',
        'Un faro solitario en la costa',
        'Una ciudad subterránea perdida',
        'Un jardín secreto en la cima de una colina',
        'Un tren abandonado en medio del desierto',
        'Un palacio flotante en las nubes',
        'Una biblioteca antigua llena de libros mágicos',
        'Un mercado de especias en una ciudad exótica',
        'Una isla tropical habitada por criaturas místicas',
        'Un castillo encantado en un bosque encantado',
        'Una estación espacial en el borde del universo',
        'Un laboratorio científico en el fondo del océano',
        'Una granja de robots en un futuro distópico',
        'Un puente colgante sobre un cañón profundo',
        'Un pueblo en las montañas donde el tiempo se mueve más despacio',
        'Una mansión encantada con pasadizos secretos',
        'Una cueva brillante llena de cristales luminosos',
        'Un campo de girasoles interminable',
        'Una estación de tren en una ciudad futurista',
        'Un circo ambulante que viaja por dimensiones',
        'Un campo de tulipanes en primavera',
        'Un oasis perdido en medio del desierto',
        'Una aldea flotante sobre un lago tranquilo',
        'Una escuela de magia en una isla remota',
        'Un mercado de pulgas en el fin del mundo',
        'Un templo antiguo en la cima de una montaña',
        'Una ciudad sumergida en las profundidades del océano',
        'Una fábrica de sueños en el país de las maravillas',
        'Un parque de atracciones abandonado',
        'Una estación de investigación en la Antártida',
        'Un pueblo en el espacio exterior',
        'Un campo de amapolas bajo la luz de la luna',
        'Un bosque encantado donde los árboles tienen ojos',
        'Una mansión victoriana llena de enigmas',
        'Un mercado de libros antiguos en una calle adoquinada',
        'Una cascada escondida en un bosque secreto',
        'Una playa con arenas que brillan en la oscuridad',
        'Un castillo de cristal en el fondo del mar',
        'Una ciudad en las nubes donde las casas flotan',
        'Un jardín de mariposas en una isla remota',
        'Una estación espacial abandonada en órbita',
        'Un observatorio astronómico en la cima de una montaña',
        'Una mansión en la niebla donde el tiempo se detiene',
        'Un mercado de especias flotante en un lago mágico',
        'Una pradera de luciérnagas en la noche',
        'Un laberinto de espejos en un mundo de ilusiones',
        'Un bosque de arcoíris con árboles de colores',
        'Una ciudad submarina construida por criaturas marinas',
        'Un jardín zen en la cima de un acantilado',
        'Una aldea habitada por seres de luz',
        'Un puente de arco iris que conecta dos mundos',
    ]
    n_details = random.randint(0, 1)
    details: list = random.sample(details, n_details)

    details_instructions = f", siempre te aseguras de poner todos los siguientes detalles en el outline: {', '.join(details).lower()}" if len(details) else ""
    stories_instructions = f" No repites historias, y te gusta mantenerte fresco y creativo, por lo tanto revisas la lista de historias creadas, para no repetir historias existentes, y usar temáticas nuevas para mantener a los lectores enganchados con la frescura de tus relatos, nunca escribes secuelas a tus historias, la lista de historias creadas hasta ahora es la siguiente: {', '.join(historias_existentes)}." if len(historias_existentes) else ""
    format_instructions = '{"outline": "aquí pones el outline, de forma seguida y continua, sin bullet points ni numeración.", "titulo": "aquí pondrás el título de la historia, debes tener en cuenta que debe ser un título muy intrigante, el cual llame la atención enseguida con solo verlo y obligue a las personas abrir la historia para saber de qué se trata. La historia será publicada online por lo que el título es extremadamente importante, piensa que será narrada en un video de youtube, por eso el título debe ser el que daría los mejores resultados para que los usuarios de youtube que lo vean den click en el video."}'

    animales_parlantes_choices = [' Siempre escribes historias que se desarrollan entre animales que hablan, sin ningún humano que forme parte de la historia.',
           ' Siempre escribes historias que se desarrollan entre animales que hablan, con un único humano que interactúa con ellos.',
           '']
    animales_parlantes_probabilities = [0.45, 0.1, 0.45]  # probabilities for each choice
    animales_parlantes = np.random.choice(animales_parlantes_choices, p=animales_parlantes_probabilities)

    longitud = " La historia va a ser leída con una duración de entre 10 a 15 minutos, por lo que debes de crear un outline adecuado para ello, ya que la historia tendrá entre 1000 y 3000 palabras, con varios párrafos." if not short else " La historia va a ser leída con una duración de 30 segundos, por lo que debes de crear un outline adecuado para ello, ya que la historia tendrá muy pocas palabras, con un único párrafo."

    messages = [
      {'role': 'system', 'content': f'Eres un chabot que crea un outline para una historia sobre una moraleja, enseñanza o lección para la vida{details_instructions}.{animales_parlantes}{longitud}\n\nDebes tener en cuenta que la historia tenga una única lección de vida o enseñanza buena para aplicar en el día a día. Utiliza un estilo misterioso para la historia, con analogías y metáforas. Evita usar clichés como que el verdadero tesoro es la amistad que forjaron en el camino. Usa nombres completamente inventados para las ubicaciones y personajes que no evoquen a otras historias o peliculas. Añade diálogos cuando creas necesario. NUNCA ESCRIBES FRASES NI ORACIONES REDUNDANTES.{tipo_de_final}{stories_instructions} Tu respuesta es en formato json, usas el siguiente formato, este formato será utilizado en python y parseado automáticamente. Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions}'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
      {'role': 'system', 'content': f'Eres un chabot que crea una historia sobre una moraleja, enseñanza o lección para la vida a partir de un outline y un título.{longitud} Expande cada tema del outline en su totalidad y con extremo detalle. El título de la historia es "{titulo}", y el outline es el siguiente: "{outline}".\n\n\nDebes tener en cuenta que la historia tenga una única lección de vida o enseñanza buena para aplicar en el día a día. Utiliza un estilo misterioso para la historia, con analogías y metáforas. Evita usar clichés como que el verdadero tesoro es la amistad que forjaron en el camino. Usa nombres completamente inventados para las ubicaciones y personajes que no evoquen a otras historias o peliculas. Añade diálogos cuando creas necesario. NUNCA ESCRIBES FRASES NI ORACIONES REDUNDANTES.{tipo_de_final} Ten en cuenta que esta es la historia final, así que no deben haber cosas descriptivas como "el protagonista", o "la historia termina con...", ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final. Nunca cometes errores ortográficos ni gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta. Tus historias siempre están escritas en tiempo pasado, nunca en tiempo presente. Tu respuesta es en formato json, usas el siguiente formato, este formato será utilizado en python y parseado automáticamente. Siempre envías el formato correcto, el cual sigue estas directrices: {format_instructions_historia}'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
    
    # Increase the length of the story if it's too short
    current_attempt = 0
    while historia and (len(re.findall(r'\b\w+\b', historia)) < 500) and not short and current_attempt < 10:
        historia = increase_length(historia)
        current_attempt += 1


    # Define the base file name
    base_filename = f'./historias/{titulo} | Cuento |  Relato |  Aventura | Superación.txt'
    base_filename_video = f'./historias_para_video/{titulo} | Cuento |  Relato |  Aventura | Superación.txt'
    base_filename_terminadas = f'./historias_terminadas/{titulo} | Cuento |  Relato |  Aventura | Superación.txt'

    # Check if the file already exists in any of the directories
    if os.path.isfile(base_filename) or os.path.isfile(base_filename_video) or os.path.isfile(base_filename_terminadas):
        # If it does, append a 'II' to the title
        filename = f'./historias/{titulo} II | Cuento |  Relato |  Aventura | Superación.txt'
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
      {'role': 'system', 'content': f'Eres un escritor famoso, tomas una historia pequeña e instantáneamente la transformas en un hit que se llena de comentarios, admiración y mucha popularidad. Para lograr eso siempre te enfocas en que las historias pequeñas sean expandidas en historias grandes, pero conversen su esencia, no cambias el tipo de historia, ni el desenlace, creas grandes escenarios y sucesos que narras con paciencia para lograr que la atmósfera atrape al lector y lo lleve al mundo de la historia como si fuera real. Siempre expandes cada oración de la historia, sin dejar ninguna oración sin haber sido expandida, para poder construir así una atmósfera completamente envolvente.{tipo_de_final} Ten en cuenta que esta es la historia final, así que no deben haber cosas descriptivas como "el protagonista", "la historia termina con...", "el relato termina con...", "dejando al lector...", etc., ya que no estás describiendo algo para alguien más, estás mostrando la historia al lector final. Nunca cometes errores ortográficos ni gramaticales en tu historia, ni siquiera en el título, toda la redacción es siempre perfecta, y siempre en idioma español sin errores de codificación. Siempre respondes en formato json, el cual es un formato perfecto y puede ser parseado directamente en python. Usas varios párrafos para dar mayor facilidad a la lectura de tus historias. El formato de tu respuesta es el siguiente: {format_instructions_historia_larga}\n\nLa historia es la siguiente:\n\n\n"{historia}"'},
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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


if __name__ == '__main__':
    main()