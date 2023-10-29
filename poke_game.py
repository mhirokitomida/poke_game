from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'poke_game'  # Adicione uma chave secreta real aqui

class Pokemon:
    def __init__(self, id, nome, stat, sprite):
        self.id=id
        self.nome=nome
        self.stat=stat
        self.sprite=sprite

def randint_exclude(start, end, exclude):
    while True:
        number = random.randint(start, end - 1)
        if number not in exclude:
            return number

data = pd.read_csv("static/database/pokemon_database.csv", sep=",")

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/higher_lower', methods=['GET', 'POST'])
def higher_lower():
    
    if request.method == 'POST':
        game_end_arg = request.form.get('game_end_arg')

        if game_end_arg:
            # Processa o game_end_arg como você já fez
            session['high_score'] = max(session['high_score'], session['score'])
            if game_end_arg == 'end':
                session['text'] = f'You correctly got right {session["score"]} Pokémons.'
                session['score_msg'] = f'Your High score is {session["high_score"]}'
            elif game_end_arg == 'end_full':
                session['text'] = "Congratulations, you're a true Pokémon Master!"
                session['score_msg'] = f'You correctly got right all {len(session["list_id"])} Pokémons.'
            
            session['battle_list'].pop()

            return redirect(url_for('higher_lower'))
    
    if 'text' in session and 'score_msg' in session:
        text = session.pop('text')
        score = session.pop('score_msg')
        battle_list = session.get('battle_list', [])
        return render_template('higher_lower_score.html', text=text, score=score, battle_list=battle_list)

    session.clear()
    
    session['score'] = 0
    if 'list_id' not in session:
        session['list_id'] = []
    if 'high_score' not in session:
        session['high_score'] = 0
       
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total']
    random_stat = random.choice(stats)
    
    # Sortear o primeiro Pokémon
    id_pkmn_1 = randint_exclude(0, len(data), session.get('list_id', []))
    nome_1 = data.loc[id_pkmn_1, 'name']
    stat_pkmn_1 = data.loc[id_pkmn_1, random_stat]
    sprite_1 = data.loc[id_pkmn_1, 'url_sprite']
    pkmn_1 = Pokemon(id_pkmn_1, nome_1, stat_pkmn_1, sprite_1)

    session['list_id'].append(id_pkmn_1)

    # Sortear o segundo Pokémon
    id_pkmn_2 = randint_exclude(0, len(data), session.get('list_id', []))
    nome_2 = data.loc[id_pkmn_2, 'name']
    stat_pkmn_2 = data.loc[id_pkmn_2, random_stat]
    sprite_2 = data.loc[id_pkmn_2, 'url_sprite']
    pkmn_2 = Pokemon(id_pkmn_2, nome_2, stat_pkmn_2, sprite_2)

    session['list_id'].append(id_pkmn_2)

    session['last_pkmn_1_id'] = id_pkmn_1
    session['last_pkmn_2_id'] = id_pkmn_2

    if 'battle_list' not in session:
        session['battle_list'] = []

    battle = battle = {
        "stat": random_stat,
        "nome1": nome_1,
        "stat1": int(stat_pkmn_1),
        "nome2": nome_2,
        "stat2": int(stat_pkmn_2)
    }
    session['battle_list'].append(battle)

    return render_template('higher_lower.html', stat=random_stat, pkmn_1=pkmn_1, pkmn_2=pkmn_2, high_score=session.get('high_score', 0))

@app.route('/resort_pokemons', methods=['GET', 'POST'])
def resort_pokemons():
    game_end = 'False'
    last_id = request.args.get('last_id')
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total']
    random_stat = random.choice(stats)

    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        id_pkmn_new = session['last_pkmn_1_id'] if last_id == 'pkmn-1' else session['last_pkmn_2_id']
    else:
        id_pkmn_new = randint_exclude(0, len(data), session.get('list_id', []))

    # Sortear um novo Pokémon
    nome_new = data.loc[id_pkmn_new, 'name']
    stat_pkmn_new = data.loc[id_pkmn_new, random_stat]
    sprite_new = data.loc[id_pkmn_new, 'url_sprite']
    novo_pokemon = Pokemon(id_pkmn_new, nome_new, stat_pkmn_new, sprite_new)
    
    session['list_id'].append(id_pkmn_new)
    session['list_id'] = list(set(session['list_id']))

    if last_id == 'pkmn-1':
        id_pkmn_old = session['last_pkmn_1_id']
        session['last_pkmn_2_id'] = id_pkmn_new
    else:
        id_pkmn_old = session['last_pkmn_2_id']
        session['last_pkmn_1_id'] = id_pkmn_new

    nome_old = data.loc[id_pkmn_old, 'name']
    stat_pkmn_old = data.loc[id_pkmn_old, random_stat]
    sprite_old = data.loc[id_pkmn_old, 'url_sprite']
    old_pokemon = Pokemon(id_pkmn_old, nome_old, stat_pkmn_old, sprite_old)

    session['score'] += 1
    if last_id == 'pkmn-1':
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
    session['battle_list'].append(battle)

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

@app.route('/reset_game', methods=['GET', 'POST'])
def reset_game():
    session.clear()  # Limpa todos os dados da sessão
    session['game_end'] = True
    return redirect(url_for('higher_lower'))

if __name__ == '__main__':
    app.run(debug=True)