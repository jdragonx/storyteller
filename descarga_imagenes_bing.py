#!/usr/bin/env python3
from openai import OpenAI
import json
import click
import os
import random
from bing_create.main import ImageGenerator
import pandas as pd

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
@click.option('--dir', '-d', default='links_bing', type=str, help='Ruta del directorio con los archivos csv con los links de las imágenes')
def main(dir):
    os.makedirs('.tmp/images', exist_ok=True)
    for file in os.listdir(dir):
        download_and_save_images_bing(os.path.join(dir,file))

def download_and_save_images_bing(file: str):

    # Read the csv file with the links of the images
    df = pd.read_csv(file)

    previous_image_path = None
    for i, row in df.iterrows():
        # Let's pick at random one of the cookies
        cookie = random.choice(cookies_bing)

        print(f"Usando cuenta: {cookie['cuenta']}")

        # Create an instance of the ImageGenerator class
        bing_image_generator = ImageGenerator(
            auth_cookie_u=cookie['auth_cookie_u'],
            auth_cookie_srchhpgusr=cookie['auth_cookie_srchhpgusr'],
            logging_enabled=False,
        )
        image_path = row['location']
        image_link = row['link']
        response = bing_image_generator.client.get(image_link)
        image = response.content
        if response.status_code != 200:
            print("Exception happened while saving image! (Response was not ok). Duplicating previous image...")
            # We duplicate the previous image
            if previous_image_path is None:
                print("There is no previous image to duplicate. Skipping...")
                continue
            with open(previous_image_path, "rb") as f:
                image = f.read()
                f.close()

        with open(image_path, "wb") as f:
            f.write(image)
            f.close()

if __name__ == '__main__':
    main()