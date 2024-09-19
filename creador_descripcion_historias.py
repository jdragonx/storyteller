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

historias_dir = "historias"
output_dir = "historias_terminadas"
descripcion_dir = "descripciones_historias"
for file in os.listdir(historias_dir):
    print("*" * 50)
    print(f"Creando descripcion para {file}")
    with open(os.path.join(historias_dir, file), "r") as f:
        historia = f.read()
        try:
            descripcion = crear_descripcion_historia(historia)
            with open(os.path.join(descripcion_dir, file), "w") as f:
                f.write(descripcion)
            os.rename(os.path.join(historias_dir, file), os.path.join(output_dir, file))
        except Exception as e:
            print(f"Error creando descripcion para {file}: {e}. Skipping...")
            traceback.print_exc()
            continue

