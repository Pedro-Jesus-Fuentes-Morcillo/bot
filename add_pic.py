#!/usr/bin/python
from PIL import Image

def add_pic(orig_file: str, png_file: str):
    # Open the background image
    orig = Image.open(orig_file)

    # Open the PNG image you want to overlay
    png = Image.open(png_file)
    # Ensure the PNG image has an alpha channel (transparency)
    png = png.convert("RGBA")

    # Resize the PNG image
    new_width, new_height = 300, 300  # Specify the desired size
    png = png.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate the position at the center of the background image
    orig_width, orig_height = orig.size
    position_x = (orig_width - new_width) // 2
    position_y = (orig_height - new_height) // 2
    position = (position_x, position_y)

    # Overlay the PNG image on the background image
    orig.paste(png, position, png)

    # Save the resulting image
    orig.save("./imgs/edits/result.jpg")
