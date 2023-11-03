# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 05:55:55 2023

@author: mauricio.tomida
"""

import os
from PIL import Image, ImageSequence

def transform_img_to_black(input_path, output_path):
    # Open the input image
    with Image.open(input_path) as im:
        # Copy all frames from the image
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]

        black_frames = []
        for frame in frames:
            # Convert each frame to RGBA
            rgba_frame = frame.convert("RGBA")
            data = list(rgba_frame.getdata())

            # Change all colors to black while preserving transparency
            black_data = [(0, 0, 0, d[3]) for d in data]
            rgba_frame.putdata(black_data)

            black_frames.append(rgba_frame)

        # Save the first frame as the output image
        black_frames[0].save(output_path, save_all=True, append_images=black_frames[1:], loop=0)

def transform_all_img_to_black(input_dir, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all files in the input directory
    for file_name in os.listdir(input_dir):
        # Construct the full path for the input and output files
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)

        # Check if it's a file and has an image file extension (e.g., '.png', '.jpg', '.jpeg', '.bmp')
        if os.path.isfile(input_path) and input_path.lower().endswith(('.png', '.jpg', '.jpeg','.bmp')):
            transform_img_to_black(input_path, output_path)
            print(f'Image transformed and saved at: {output_path}')
    
# Convert all imgs to black
gens = ['gen_I', 'gen_II', 'gen_III', 'gen_IV', 'gen_V', 'gen_VI', 'gen_VII', 'gen_VIII']    
for gen in gens:
    # Define the input and output directory paths
    input_dir = 'sprites/' + gen
    output_dir = 'shadow_sprites/' + gen

    transform_all_img_to_black(input_dir, output_dir)