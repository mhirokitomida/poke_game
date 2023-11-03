from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import pandas as pd
import random
import json

app = Flask(__name__)
app.secret_key = 'poke_game'  # Adicione uma chave secreta real aqui

class Pokemon:
    def __init__(self, id, nome, stat, sprite, shadow_sprite = None):
        self.id=id
        self.nome=nome
        self.stat=stat
        self.sprite=sprite
        self.shadow_sprite=shadow_sprite

def randint_exclude(start, end, exclude):
    while True:
        number = random.randint(start, end)
        if number not in exclude:
            return number
        
def clean_session():
    session.pop('score', None)
    session.pop('text', None)
    session.pop('score_msg', None)
    session.pop('pkmn_list', None)
    session.pop('list_id', None)
    session.pop('last_pkmn_id', None)
    session.pop('last_pkmn_2_id', None)

data_full = pd.read_csv("https://raw.githubusercontent.com/mhirokitomida/poke_game/main/data/database/pokemon_database.csv", sep=",")

@app.route('/')
def index():
    clean_session()
    session.pop('gen', None)
    session.pop('atributes', None)
    session.pop('data', None)
    return render_template('index.html')

@app.route('/higher_lower_home', methods=['GET', 'POST'])
def higher_lower_home():
    clean_session()
    session.pop('gen', None)
    session.pop('atributes', None)
    session.pop('data', None)
    return render_template('higher_lower_home.html')

@app.route('/higher_lower', methods=['GET', 'POST'])
def higher_lower():

    if request.method == 'POST':
        if 'gen' not in session and 'atributes' not in session:
            session['gen']  = request.form.getlist('gen[]')
            session['atributes'] = request.form.getlist('atributes[]')
        
        game_end_arg = request.form.get('game_end_arg')
        if game_end_arg:
            generation = session.get('gen', data_full['generation'].unique().tolist())
            data = data_full.query('generation in @generation')
            if game_end_arg == 'end':
                session['text'] = f'You correctly got right {session["score"]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
                if session.get('score', 0) > session['high_score_hl']:
                    session['high_score_hl'] = max(session['high_score_hl'], session['score'])
                    session['text'] = f'Congratulations, you have a new High Score: {session["high_score_hl"]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
                    session['score_msg'] = ""
                else:
                    session['score_msg'] = f'Your High score is {session["high_score_hl"]} Pokémons.'
            elif game_end_arg == 'end_full':
                session['high_score_hl'] = max(session['high_score_hl'], session['score'])
                session['text'] = "Congratulations, you're a true Pokémon Master!"
                session['score_msg'] = f'You correctly got right all {len(session["list_id"])} Pokémons.'
            
            session['pkmn_list'].pop()

            return redirect(url_for('higher_lower'))
    
    if 'text' in session and 'score_msg' in session:
        text = session.pop('text')
        score = session.pop('score_msg')
        pkmn_list = session.get('pkmn_list', [])
        return render_template('higher_lower_score.html', text=text, score=score, pkmn_list=pkmn_list)

    clean_session()

    session['score'] = 0
    session['high_score_hl'] = session.get('high_score_hl', 0)
    if 'list_id' not in session:
        session['list_id'] = []
    
    stats = session.get('atributes', ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total'])
    random_stat = random.choice(stats)

    generation = session.get('gen', data_full['generation'].unique().tolist())
    data = data_full.query('generation in @generation')

    # Sortear o primeiro Pokémon
    id_pkmn = randint_exclude(min(data['id']), max(data['id']), session.get('list_id', []))
    nome_1 = data.loc[id_pkmn, 'name']
    stat_pkmn = data.loc[id_pkmn, random_stat]
    sprite_1 = data.loc[id_pkmn, 'url_sprite']
    pkmn = Pokemon(id_pkmn, nome_1, stat_pkmn, sprite_1)

    session['list_id'].append(id_pkmn)

    # Sortear o segundo Pokémon
    id_pkmn_2 = randint_exclude(min(data['id']), max(data['id']), session.get('list_id', []))
    nome_2 = data.loc[id_pkmn_2, 'name']
    stat_pkmn_2 = data.loc[id_pkmn_2, random_stat]
    sprite_2 = data.loc[id_pkmn_2, 'url_sprite']
    pkmn_2 = Pokemon(id_pkmn_2, nome_2, stat_pkmn_2, sprite_2)

    session['list_id'].append(id_pkmn_2)

    session['last_pkmn_id'] = id_pkmn
    session['last_pkmn_2_id'] = id_pkmn_2

    if 'pkmn_list' not in session:
        session['pkmn_list'] = []

    battle = battle = {
        "stat": random_stat,
        "nome1": nome_1,
        "stat1": int(stat_pkmn),
        "nome2": nome_2,
        "stat2": int(stat_pkmn_2)
    }
    session['pkmn_list'].append(battle)

    return render_template('higher_lower.html', stat=random_stat, pkmn=pkmn, pkmn_2=pkmn_2, high_score_hl=session.get('high_score_hl', 0))

@app.route('/resort_pokemons_hl', methods=['GET', 'POST'])
def resort_pokemons_hl():
    game_end = 'False'
    last_id = request.args.get('last_id')
    stats = session.get('atributes', ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total'])
    random_stat = random.choice(stats)
    generation = session.get('gen', data_full['generation'].unique().tolist())
    data = data_full.query('generation in @generation')

    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        id_pkmn_new = session['last_pkmn_id'] if last_id == 'pkmn' else session['last_pkmn_2_id']
    else:
        id_pkmn_new = randint_exclude(min(data['id']), max(data['id']), session.get('list_id', []))

    # Sortear um novo Pokémon
    nome_new = data.loc[id_pkmn_new, 'name']
    stat_pkmn_new = data.loc[id_pkmn_new, random_stat]
    sprite_new = data.loc[id_pkmn_new, 'url_sprite']
    novo_pokemon = Pokemon(id_pkmn_new, nome_new, stat_pkmn_new, sprite_new)

    session['list_id'].append(id_pkmn_new)
    session['list_id'] = list(set(session['list_id']))

    if last_id == 'pkmn':
        id_pkmn_old = session['last_pkmn_id']
        session['last_pkmn_2_id'] = id_pkmn_new
    else:
        id_pkmn_old = session['last_pkmn_2_id']
        session['last_pkmn_id'] = id_pkmn_new

    nome_old = data.loc[id_pkmn_old, 'name']
    stat_pkmn_old = data.loc[id_pkmn_old, random_stat]
    sprite_old = data.loc[id_pkmn_old, 'url_sprite']
    old_pokemon = Pokemon(id_pkmn_old, nome_old, stat_pkmn_old, sprite_old)

    session['score'] += 1
    if last_id == 'pkmn':
        battle = {
        "stat": random_stat,
        "nome1": nome_old,
        "stat1": int(stat_pkmn_old),
        "nome2": nome_new,
        "stat2": int(stat_pkmn_new)
        }
    else:
        battle = {
        "stat": random_stat,
        "nome1": nome_new,
        "stat1": int(stat_pkmn_new),
        "nome2": nome_old,
        "stat2": int(stat_pkmn_old)
        }
    session['pkmn_list'].append(battle)

    return jsonify({
        'game_end': game_end,
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

@app.route('/reset_game_hl', methods=['GET', 'POST'])
def reset_game_hl():
    clean_session()
    return redirect(url_for('higher_lower'))

@app.route('/reset_game_full_hl', methods=['GET', 'POST'])
def reset_game_full_hl():
    clean_session()
    session.pop('gen', None)
    session.pop('atributes', None)
    session.pop('data', None)

    return redirect(url_for('higher_lower_home'))


@app.route('/whos_that_pkmn_home', methods=['GET', 'POST'])
def whos_that_pkmn_home():
    clean_session()
    return render_template('whos_that_pkmn_home.html')

@app.route('/whos_that_pkmn', methods=['GET', 'POST'])
def whos_that_pkmn():

    if request.method == 'POST':
        if 'gen' not in session:
            session['gen']  = request.form.getlist('gen[]')
        
        game_end_arg = request.form.get('game_end_arg')
        if game_end_arg:
            generation = session.get('gen', data_full['generation'].unique().tolist())
            data = data_full.query('generation in @generation')
            if game_end_arg == 'end':
                session['text'] = f'You correctly got right {session["score"]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
                if session.get('score', 0) > session['high_score_wtp']:
                    session['high_score_wtp'] = max(session['high_score_wtp'], session['score'])
                    session['text'] = f'Congratulations, you have a new High Score: {session["high_score_wtp"]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
                    session['score_msg'] = ""
                else:
                    session['score_msg'] = f'Your High score is {session["high_score_wtp"]} Pokémons.'
            elif game_end_arg == 'end_full':
                session['high_score_wtp'] = max(session['high_score_wtp'], session['score'])
                session['text'] = "Congratulations, you're a true Pokémon Master!"
                session['score_msg'] = f'You correctly got right all {len(session["list_id"])} Pokémons.'
            
            session['pkmn_list'].pop()

            return redirect(url_for('whos_that_pkmn'))
    
    if 'text' in session and 'score_msg' in session:
        text = session.pop('text')
        score = session.pop('score_msg')
        pkmn_list = session.get('pkmn_list', [])
        return render_template('whos_that_pkmn_score.html', text=text, score=score, pkmn_list=pkmn_list)

    clean_session()

    session['score'] = 0
    session['high_score_wtp'] = session.get('high_score_wtp', 0)
    if 'list_id' not in session:
        session['list_id'] = []
    
    generation = session.get('gen', data_full['generation'].unique().tolist())
    data = data_full.query('generation in @generation')

    # Sortear o primeiro Pokémon
    id_pkmn = randint_exclude(min(data['id']), max(data['id']), session.get('list_id', []))
    nome = data.loc[id_pkmn, 'name']
    sprite = data.loc[id_pkmn, 'url_sprite']
    shadow_sprite = data.loc[id_pkmn, 'url_shadow_sprite']
    pkmn = Pokemon(id_pkmn, nome, None, sprite, shadow_sprite)

    session['list_id'].append(id_pkmn)

    if 'pkmn_list' not in session:
        session['pkmn_list'] = []

    guessed_pkmn = guessed_pkmn = {
        "nome": nome,
        "generation": data.loc[id_pkmn, 'generation']
    }
    session['pkmn_list'].append(guessed_pkmn)

    generations_dict = data.groupby('generation')['name'].apply(list).to_dict()

    return render_template('whos_that_pkmn.html', pkmn=pkmn, generations_dict = generations_dict, high_score_wtp=session.get('high_score_wtp', 0))

@app.route('/resort_pokemons_wtp', methods=['GET', 'POST'])
def resort_pokemons_wtp():
    game_end = 'False'
    generation = session.get('gen', data_full['generation'].unique().tolist())
    data = data_full.query('generation in @generation')

    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        id_pkmn_new = session['list_id'][0]
    else:
        id_pkmn_new = randint_exclude(min(data['id']), max(data['id']), session.get('list_id', []))

    # Sortear um novo Pokémon
    nome_new = data.loc[id_pkmn_new, 'name']
    sprite_new = data.loc[id_pkmn_new, 'url_sprite']
    shadow_sprite_new = data.loc[id_pkmn_new, 'url_shadow_sprite']
    novo_pokemon = Pokemon(id_pkmn_new, nome_new, None, sprite_new, shadow_sprite_new)

    print(novo_pokemon.nome)
    print(game_end)

    session['list_id'].append(id_pkmn_new)
    session['list_id'] = list(set(session['list_id']))

    session['score'] += 1
    guessed_pkmn = guessed_pkmn = {
        "nome": nome_new,
        "generation": data.loc[id_pkmn_new, 'generation']
    }
    session['pkmn_list'].append(guessed_pkmn)

    return jsonify({
        'game_end': game_end,
        'id': novo_pokemon.id,
        'nome': novo_pokemon.nome,
        'sprite': novo_pokemon.sprite,
        'shadow_sprite': novo_pokemon.shadow_sprite
    })

@app.route('/reset_game_wtp', methods=['GET', 'POST'])
def reset_game_wtp():
    clean_session()
    return redirect(url_for('whos_that_pkmn'))

@app.route('/reset_game_full_wtp', methods=['GET', 'POST'])
def reset_game_full_wtp():
    clean_session()
    session.pop('gen', None)
    session.pop('data', None)

    return redirect(url_for('whos_that_pkmn_home'))

if __name__ == '__main__':
    app.run(debug=True)