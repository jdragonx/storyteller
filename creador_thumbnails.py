#!/usr/bin/env python3
import click
import os
from PIL import Image, ImageDraw, ImageFont
import traceback

@click.command()
@click.option('--file', '-f', type=str, help='Ruta del archivo de la imagen para crear el thumbnail')
@click.option('--dir', '-d', type=str, default='imagenes_thumbnail', help='Ruta del directorio de las imágenes para crear los thumbnails')
def main(file, dir):
    os.makedirs('.tmp/thumbnails', exist_ok=True)
    if file:
        try:
            create_thumbnail(file)
        except Exception as e:
            print(f"Error creando thumbnail para {file}: {e}. Exiting...")
            return
    else:
        for file in os.listdir(dir):
            print("*" * 50)
            print(f"Creando thumbnail para {file}")
            try:
                create_thumbnail(os.path.join(dir, file))
            except Exception as e:
                print(f"Error creando thumbnail para {file}: {e}. Skipping...")
                traceback.print_exc()
                continue

def split_text(text, draw, font, max_width):
    if draw.textlength(text, font=font) <= max_width:
        return text

    middle = len(text) // 2
    split_index = middle
    while split_index > 0 and text[split_index] != ' ':
        split_index -= 1

    if split_index == 0:  # No space found to the left of the middle
        split_index = middle
        while split_index < len(text) and text[split_index] != ' ':
            split_index += 1

    if split_index == len(text):  # No space found to the right of the middle
        split_index = middle  # Split in the middle

    if text[split_index] == ' ':  # If the split index is at a space, increment it
        split_index += 1

    line1 = text[:split_index]
    line2 = text[split_index:]

    return split_text(line1, draw, font, max_width) + '\n' + split_text(line2, draw, font, max_width)

def crop_image(image):
    # Calculate target size based on 16:9 aspect ratio
    width, height = image.size
    target_aspect = 16 / 9
    current_aspect = width / height

    if current_aspect > target_aspect:
        # If image is wider than target aspect, adjust width
        new_width = int(target_aspect * height)
        left = (width - new_width) / 2
        right = (width + new_width) / 2
        top = 0
        bottom = height
    else:
        # If image is taller than target aspect, adjust height
        new_height = int(width / target_aspect)
        top = (height - new_height) / 2
        bottom = (height + new_height) / 2
        left = 0
        right = width

    # Crop the image to 16:9
    return image.crop((left, top, right, bottom))

def create_thumbnail(file: str):
    # Open the image file
    image = Image.open(file)

    # Crop the image to 16:9 aspect ratio
    image = crop_image(image)

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Create a font object with a larger size, say 25
    font = ImageFont.truetype('/home/jdragonx/storyteller/fonts/dejavu-sans/DejaVuSans-Bold.ttf', 80)

    # Get the filename without extension
    text = os.path.splitext(os.path.basename(file))[0]

    # Split the text into multiple lines if it exceeds the set width
    text = split_text(text, draw, font, image.width / 2)

    text_position = (20, 20)

    # Draw the text on the image with black color to create a border
    for x_offset in range(-3, 4):
        for y_offset in range(-3, 4):
            draw.multiline_text((text_position[0] + x_offset, text_position[1] + y_offset), text, font=font, fill='black')

    # Draw the text on the image with a dark red color
    draw.multiline_text(text_position, text, font=font, fill='red')

    # Save the image with maximum quality
    output_file_path = f'.tmp/thumbnails/{os.path.basename(file)}'
    quality = 100
    image.save(output_file_path, quality=quality)

    # Check the file size and reduce quality if necessary
    while os.path.getsize(output_file_path) > 2 * 1024 * 1024:  # 2MB
        quality -= 5  # reduce quality by 5
        image.save(output_file_path, quality=quality)

if __name__ == "__main__":
    main()
