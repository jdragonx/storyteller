#!/usr/bin/env python3
import math
import time
import traceback
import json
import click
import os
import random
from bing_create.main import ImageGenerator
import pandas as pd

max_retries = 15

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
        
        retry_count = 0
        while retry_count < max_retries:
            try:
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
                break
            except Exception as e:
                print(f"Error creating image: {e}. Retrying...")
                traceback.print_exc()
                retry_count += 1
                backoff_time = math.pow(1.5, retry_count)  # exponential backoff
                time.sleep(backoff_time)  # pause execution for backoff_time seconds
        if retry_count >= max_retries:
            print("Max retries reached trying to download image. Exiting...")
            exit(1) 
if __name__ == '__main__':
    main()