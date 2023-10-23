from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import pandas as pd
import random

class Pokemon:
    def __init__(self, id, nome, stat, sprite):
        self.id=id
        self.nome=nome
        self.stat=stat
        self.sprite=sprite

def randint_exclude(start, end, exclude):
    while True:
        number = random.randint(start, end)
        if number not in exclude:
            return number

data = pd.read_csv("static/database/pokemon_database.csv", sep=",")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Armazenando o último Pokémon que foi acertado
list_id = []
last_pkmn_1_id = None
last_pkmn_2_id = None

@app.route('/higher_lower')
def higher_lower():
    global last_pkmn_1_id, last_pkmn_2_id, list_id

    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total']
    random_stat = random.choice(stats)

    # Sortear o primeiro Pokémon
    id_pkmn_1 = randint_exclude(1, len(data), list_id)
    nome_1 = data.loc[id_pkmn_1, 'name']
    stat_pkmn_1 = data.loc[id_pkmn_1, random_stat]
    sprite_1 = data.loc[id_pkmn_1, 'url_sprite']
    pkmn_1 = Pokemon(id_pkmn_1, nome_1, stat_pkmn_1, sprite_1)

    list_id.append(id_pkmn_1)

    # Sortear o segundo Pokémon
    id_pkmn_2 = randint_exclude(1, len(data), list_id)
    nome_2 = data.loc[id_pkmn_2, 'name']
    stat_pkmn_2 = data.loc[id_pkmn_2, random_stat]
    sprite_2 = data.loc[id_pkmn_2, 'url_sprite']
    pkmn_2 = Pokemon(id_pkmn_2, nome_2, stat_pkmn_2, sprite_2)

    list_id.append(id_pkmn_2)

    last_pkmn_1_id = id_pkmn_1
    last_pkmn_2_id = id_pkmn_2

    return render_template('higher_lower.html', stat=random_stat, pkmn_1=pkmn_1, pkmn_2=pkmn_2)

@app.route('/resort_pokemons')
def resort_pokemons():
    global last_pkmn_1_id, last_pkmn_2_id, list_id

    last_id = request.args.get('last_id')
    
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total']
    random_stat = random.choice(stats)

    # Sortear um novo Pokémon
    id_pkmn_new = randint_exclude(1, len(data), list_id)
    nome_new = data.loc[id_pkmn_new, 'name']
    stat_pkmn_new = data.loc[id_pkmn_new, random_stat]
    sprite_new = data.loc[id_pkmn_new, 'url_sprite']
    novo_pokemon = Pokemon(id_pkmn_new, nome_new, stat_pkmn_new, sprite_new)

    if last_id == 'pkmn-1':
        id_pkmn_old = last_pkmn_1_id
        last_pkmn_2_id = id_pkmn_new
    else:
        id_pkmn_old = last_pkmn_2_id
        last_pkmn_1_id = id_pkmn_new
    
    list_id.append(id_pkmn_new)

    nome_old = data.loc[id_pkmn_old, 'name']
    stat_pkmn_old = data.loc[id_pkmn_old, random_stat]
    sprite_old = data.loc[id_pkmn_old, 'url_sprite']
    old_pokemon = Pokemon(id_pkmn_old, nome_old, stat_pkmn_old, sprite_old)

    return jsonify({
        'random_stat': random_stat,
        'novo_pokemon': {
            'id': novo_pokemon.id,
            'nome': novo_pokemon.nome,
            'stat': int(novo_pokemon.stat),
            'sprite': novo_pokemon.sprite
        },
        'old_pokemon': {
            'id': old_pokemon.id,
            'nome': old_pokemon.nome,
            'stat': int(old_pokemon.stat),
            'sprite': old_pokemon.sprite
        }
    })


app.run(debug=True)