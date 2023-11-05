from flask import Blueprint, render_template, session, request, jsonify
import random
from ..models import Pokemon
from ..utils import sort_pkmn, clean_session, game_end, get_data_full, get_all_generations, get_all_stats

generations = get_all_generations()
all_generations = get_all_generations()
all_stats = get_all_stats()

higher_lower_bp = Blueprint('higher_lower', __name__, template_folder='../templates')

@higher_lower_bp.route('/higher_lower_home', methods=['GET', 'POST'])
def home():
    clean_session('all')
    return render_template('higher_lower_home.html')

@higher_lower_bp.route('/higher_lower', methods=['GET', 'POST'])
def start_game():
    data_full = get_data_full()
    if request.method == 'POST':
        if 'gen' not in session and 'atributes' not in session:
            session['gen']  = request.form.getlist('gen[]')
            session['atributes'] = request.form.getlist('atributes[]')

        result = game_end('hl')
        if result:
            return result

    clean_session('reset_hl')

    session['score'] = 0
    session['high_score_hl'] = session.get('high_score_hl', 0)
    session['list_id'] = session.get('list_id', [])
    
    stats = session.get('atributes', all_stats)
    random_stat = random.choice(stats)

    generation = session.get('gen', all_generations)
    data = data_full.query('generation in @generation')

    # Sortear o primeiro Pokémon
    pkmn_1 = sort_pkmn(data, random_stat)

    # Sortear o segundo Pokémon
    pkmn_2 = sort_pkmn(data, random_stat)

    session['last_pkmn_1_id'] = pkmn_1.id
    session['last_pkmn_2_id'] = pkmn_2.id

    session['pkmn_list'] = session.get('pkmn_list', [])

    battle = battle = {
        "stat": random_stat,
        "nome1": pkmn_1.nome,
        "stat1": int(pkmn_1.stat),
        "nome2": pkmn_2.nome,
        "stat2": int(pkmn_2.stat)
    }
    session['pkmn_list'].append(battle)

    return render_template('higher_lower.html', stat=random_stat, pkmn_1=pkmn_1, pkmn_2=pkmn_2, high_score_hl=session.get('high_score_hl', 0))

@higher_lower_bp.route('/resort_pokemons_hl', methods=['GET', 'POST'])
def resort_pokemons():
    data_full = get_data_full()
    game_end = 'False'
    last_id = request.args.get('last_id')
    stats = session.get('atributes', all_stats)
    random_stat = random.choice(stats)
    generation = session.get('gen', all_generations)
    data = data_full.query('generation in @generation')

    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        return jsonify({
        'game_end': game_end
        })

    # Sortear um novo Pokémon
    novo_pokemon = sort_pkmn(data, random_stat)

    if last_id == 'pkmn-1':
        id_pkmn_old = session['last_pkmn_1_id']
        session['last_pkmn_2_id'] = novo_pokemon.id
    else:
        id_pkmn_old = session['last_pkmn_2_id']
        session['last_pkmn_1_id'] = novo_pokemon.id

    nome_old = data.loc[id_pkmn_old, 'name']
    stat_pkmn_old = data.loc[id_pkmn_old, random_stat]
    sprite_old = data.loc[id_pkmn_old, 'url_sprite']
    old_pokemon = Pokemon(id_pkmn_old, nome_old, stat_pkmn_old, sprite_old)

    session['score'] += 1
    if last_id == 'pkmn-1':
        battle = {
        "stat": random_stat,
        "nome1": old_pokemon.nome,
        "stat1": int(old_pokemon.stat),
        "nome2": novo_pokemon.nome,
        "stat2": int(novo_pokemon.stat)
        }
    else:
        battle = {
        "stat": random_stat,
        "nome1": novo_pokemon.nome,
        "stat1": int(novo_pokemon.stat),
        "nome2": old_pokemon.nome,
        "stat2": int(old_pokemon.stat)
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
    
