# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 20:27:55 2023

@author: mauricio.tomida
"""

import requests
import pandas as pd
import numpy as np

########################################
################ Sprites ###############
########################################

# Constants for the repository
REPO_OWNER = "mhirokitomida"
REPO_NAME = "poke_game"
BRANCH = "main"

def list_img_files_in_repository(owner, repo, branch, sprite_folder_prefix):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = requests.get(url)
    response.raise_for_status()

    # List comprehension to filter png files inside the specified sprites folder
    files = [file['path'] for file in response.json()['tree'] 
             if file['path'].startswith(sprite_folder_prefix) and file['path'].endswith('.png')]

    return files

def generate_raw_url(owner, repo, branch, filepath):
    return f"https://github.com/{owner}/{repo}/blob/{branch}/{filepath}?raw=true"

SPRITE_FOLDER_PREFIX = "data/images/sprites/"
img_files = list_img_files_in_repository(REPO_OWNER, REPO_NAME, BRANCH, SPRITE_FOLDER_PREFIX)
filenames = [filepath.split('/')[-1] for filepath in img_files]
raw_urls = [generate_raw_url(REPO_OWNER, REPO_NAME, BRANCH, filepath) for filepath in img_files]
df_sprite = pd.DataFrame({'id': filenames, 'url_sprite': raw_urls})
df_sprite['id'] = df_sprite['id'].str.replace('.png', '')

SHADOW_SPRITE_FOLDER_PREFIX = "data/images/shadow_sprites/"
img_files = list_img_files_in_repository(REPO_OWNER, REPO_NAME, BRANCH, SHADOW_SPRITE_FOLDER_PREFIX)
filenames = [filepath.split('/')[-1] for filepath in img_files]
raw_urls = [generate_raw_url(REPO_OWNER, REPO_NAME, BRANCH, filepath) for filepath in img_files]
df_sprite_shadow = pd.DataFrame({'id': filenames, 'url_shadow_sprite': raw_urls})
df_sprite_shadow['id'] = df_sprite['id'].str.replace('.png', '')

df_sprite = pd.merge(df_sprite, df_sprite_shadow, on='id', how='inner')

df_sprite['id'] = pd.to_numeric(df_sprite['id'])
df_sprite.sort_values('id', inplace = True)
df_sprite = df_sprite.reset_index(drop = True)

########################################

########################################
############# Pokeapi data #############
########################################

from get_data_pokeapi import PokemonData

df_pokemon_info = pd.DataFrame()

for i in range(1, len(df_sprite) + 1):
    print(f'Searching pokemon id = {i}...')
    pokemon = PokemonData(i)
    result_df = pokemon.basic_info().loc[:,['id', 'name', 'generation', 'height', 'weight']]
    result_df = pd.concat([result_df, pokemon.stats_info()], axis=1)
    df_pokemon_info = pd.concat([df_pokemon_info, result_df], ignore_index=True)
    
df_pokemon_info['name'] = df_pokemon_info['name'].apply(lambda x: x.title())

########################################

########################################
############ Export to .csv ############
########################################

# Merge sprites 
df_result = pd.merge(df_pokemon_info, df_sprite, on='id', how='inner')

# Conveting None to nan
df_result.replace({None: np.nan}, inplace=True)

# Export to .csv
df_result.to_csv('pokemon_database.csv', index=False)