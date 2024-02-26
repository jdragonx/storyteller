#!/usr/bin/env python3
import click
import json
from openai import OpenAI

@click.command()
@click.option('--documento', '-d', type=str, help='Documento a traducir')
def main(documento: str):
    client = OpenAI()
    with open(documento, 'r') as f:
        texto = f.read()
        texto_parrafos = texto.split('\n')

        # Ahora juntamos los parrafos en grupos de 10
        texto_parrafos = ['\n'.join(texto_parrafos[i:i+10]) for i in range(0, len(texto_parrafos), 10)]
        traducciones = []
        for parrafo in texto_parrafos:
            try:
                messages = [
                {'role': 'system', 'content': f'Eres un chabot que encarga de traducir una sección de una historia que recibe al español en su TOTALIDAD, nunca traduces solo un parte, siempre traduces el texto de forma COMPLETA. Tu respuesta es únicamente la sección de la traducida, sin conversaciones, sin preguntas y sin ningún tipo de alución al usuario.'},
                {'role': 'user', 'content': parrafo}
                ]
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=messages,
                    temperature=0,
                    seed=7,
                )
                traducciones.append(response.choices[0].message.content)
            except Exception as e:
                print(f"Error creating chat completion: {e}")
                return
        with open(documento.replace('.txt', '_traducido.txt'), 'w') as f:
            f.write('\n'.join(traducciones))

if __name__ == '__main__':
    main()