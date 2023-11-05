from flask import Blueprint, render_template, session, request, jsonify
from ..utils import sort_pkmn, clean_session, game_end, get_data_full, get_all_generations, get_all_stats

generations = get_all_generations()
all_generations = get_all_generations()
all_stats = get_all_stats()

wtp_bp = Blueprint('whos_that_pkmn', __name__, template_folder='../templates')

@wtp_bp.route('/whos_that_pkmn_home', methods=['GET', 'POST'])
def home():
    clean_session('all')
    return render_template('whos_that_pkmn_home.html')

@wtp_bp.route('/whos_that_pkmn', methods=['GET', 'POST'])
def start_game():
    data_full = get_data_full()
    if request.method == 'POST':
        if 'gen' not in session:
            session['gen']  = request.form.getlist('gen[]')
        
        result = game_end('wtp')
        if result:
            return result
    
    clean_session('reset_wtp')

    session['score'] = 0
    session['high_score_wtp'] = session.get('high_score_wtp', 0)
    session['list_id'] = session.get('list_id', [])
    
    generation = session.get('gen', all_generations)
    data = data_full.query('generation in @generation')

    # Sortear o primeiro Pokémon
    pkmn = sort_pkmn(data)

    session['pkmn_list'] = session.get('pkmn_list', [])

    guessed_pkmn = guessed_pkmn = {
        "nome": pkmn.nome,
        "generation": data.loc[pkmn.id, 'generation']
    }
    session['pkmn_list'].append(guessed_pkmn)

    generations_dict = data.groupby('generation')['name'].apply(list).to_dict()

    return render_template('whos_that_pkmn.html', pkmn=pkmn, generations_dict = generations_dict, high_score_wtp=session.get('high_score_wtp', 0))

@wtp_bp.route('/resort_pokemons_wtp', methods=['GET', 'POST'])
def resort_pokemons():
    data_full = get_data_full()
    game_end = 'False'
    generation = session.get('gen', all_generations)
    data = data_full.query('generation in @generation')

    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        return jsonify({'game_end': game_end})

    # Sortear um novo Pokémon
    novo_pokemon = sort_pkmn(data)

    session['score'] += 1
    guessed_pkmn = guessed_pkmn = {
        "nome": novo_pokemon.nome,
        "generation": data.loc[novo_pokemon.id, 'generation']
    }
    session['pkmn_list'].append(guessed_pkmn)

    return jsonify({
        'game_end': game_end,
        'id': novo_pokemon.id,
        'nome': novo_pokemon.nome,
        'sprite': novo_pokemon.sprite,
        'shadow_sprite': novo_pokemon.shadow_sprite
    })