# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 03:32:23 2023

@author: mauricio.tomida
"""

import requests
from bs4 import BeautifulSoup
import os

# Fuction to WebScrap IMG's from https://projectpokemon.org/
def pokemon_scrapper(url, path, list_pkmn_form):    
    # Get page content
    response = requests.get(url)
    response.raise_for_status()
    
    # BeautifulSoup instance
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all images .png in the page
    imgs_full = [img['src'] for img in soup.find_all('img') if 'png' in img['src'].lower()][1:]
    imgs_full = [item for item in imgs_full if 'poke_capture' in item]    
    imgs = [img.split('/')[-1] for img in imgs_full]
    sprites_types = list(set([item.split('_')[-4] + "_" + item.split('_')[-2] + "_" + item.split('_')[-1].split('.')[0] + "_v" + str(int(item.split('_')[-6]))  for item in imgs]))
    sprites_types = [item for item in sprites_types if item in list_pkmn_form]    
    
    # Create all directory to save the differents pokemon form
    for sprite_type in sprites_types:
        sprite_type_path = f'{path}/{sprite_type}'
        # Check if directory exist
        existe_dir = os.path.exists(sprite_type_path)
        if not existe_dir:
           # Create directory, if doesnt exist
           os.makedirs(sprite_type_path)
           print(f'Create new directory "/{sprite_type_path}"')
    
    # Download imgs
    print("\nStart download imgs...")
    for img in imgs_full:
        img_url = img.split('/')[-1]
        # sprite_path
        sprite_path = img_url.split('_')[-4] + "_" + img_url.split('_')[-2] + "_" + img_url.split('_')[-1].split('.')[0] + "_v" + str(int(img_url.split('_')[-6]))
        
        if sprite_path not in list_pkmn_form:
            continue
        
        # Extrai o nome do pokemon
        pokemon_id = int(img_url.split('_')[-7])
    
        with open(f'{path}/{sprite_path}/{pokemon_id}.png', 'wb') as f:
            f.write(requests.get(img).content)
        
        print(f"Download: {pokemon_id}")
    
    print("All the images have been downloaded!")
    
# List here all pokemon form
list_pkmn_form = ['n_f_n_v0']
    
# GEN I
url_1 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-1-r128/"
path_1 = "sprites/gen_I"
pokemon_scrapper(url_1, path_1, list_pkmn_form)

# GEN II
url_2 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-2-r129/"
path_2 = "sprites/gen_II"
pokemon_scrapper(url_2, path_2, list_pkmn_form)

# GEN III
url_3 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-3-r130/"
path_3 = "sprites/gen_III"
pokemon_scrapper(url_3, path_3, list_pkmn_form)

# GEN IV
url_4 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-4-r131/"
path_4 = "sprites/gen_IV"
pokemon_scrapper(url_4, path_4, list_pkmn_form)

# GEN V
url_5 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-5-r132/"
path_5 = "sprites/gen_V"
pokemon_scrapper(url_5, path_5, list_pkmn_form)

# GEN VI
url_6 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-6-r133/"
path_6 = "sprites/gen_VI"
pokemon_scrapper(url_6, path_6, list_pkmn_form)

# GEN VII
url_7 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-7-r134/"
path_7 = "sprites/gen_VII"
pokemon_scrapper(url_7, path_7, list_pkmn_form)

# GEN VIII
url_8 = "https://projectpokemon.org/home/docs/spriteindex_148/home-sprites-gen-8-r135/"
path_8 = "sprites/gen_VIII"
pokemon_scrapper(url_8, path_8, list_pkmn_form)
