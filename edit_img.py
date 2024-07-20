#!/usr/bin/python
from PIL import Image
import os

from constants import (
    BASE_DIR, DATA_DIR,
    MEDIA_DIR, CACHE_FILE_PATH,
    VIDEO_DIR, IMAGE_DIR,
    GIF_DIR, VOICE_DIR,
    EDITS_DIR
)

def add_pic(orig_file: str, png_file: str):
    '''Overlay a PNG file on another pic'''
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
    result_path = os.path.join(EDITS_DIR, 'result.jpg')
    orig.save(result_path)

def apply_filter(orig_file: str, filter_file: str):
    '''Overlay a filter PNG file on another pic'''
    # Open the background image
    orig = Image.open(orig_file)

    # Open the PNG image you want to overlay
    filter_img = Image.open(filter_file)
    # Ensure the PNG image has an alpha channel (transparency)
    filter_img = filter_img.convert("RGBA")

    orig_width, orig_height = orig.size
    filter_img = filter_img.resize((orig_width, orig_height), Image.Resampling.LANCZOS)

    # Superpose filter over original image
    orig.paste(filter_img, (0, 0), filter_img)

    # Save the resulting image
    result_path = os.path.join(EDITS_DIR, 'result.jpg')
    orig.save(result_path)
