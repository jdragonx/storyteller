#!/usr/bin/env python3
import math
import time
import traceback
import click
import os
import requests
import pandas as pd

max_retries = 17

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
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                image_path = row['location']
                image_link = row['link']
                response = requests.get(image_link)
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
                backoff_time = math.pow(2, retry_count)  # exponential backoff
                time.sleep(backoff_time)  # pause execution for backoff_time seconds
        if retry_count >= max_retries:
            print("Max retries reached trying to download image. Exiting...")
            exit(1) 
if __name__ == '__main__':
    main()