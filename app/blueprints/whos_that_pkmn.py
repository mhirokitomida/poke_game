from flask import Blueprint, render_template, session, request, jsonify
from ..utils import sort_pkmn, clean_session, game_end, get_data_full, get_all_generations

# Blueprint for the Who's That Pokémon game views and logic
wtp_bp = Blueprint('whos_that_pkmn', __name__, template_folder='../templates')

# Retrieve all available generations from configuration (config.py)
all_generations = get_all_generations()

# Serve the home page for the Who's That Pokémon game, which includes instructions and settings.
# Also, clear any existing game session data to ensure a fresh start for the user.
@wtp_bp.route('/whos_that_pkmn_home', methods=['GET', 'POST'])
def home():
    clean_session('all')
    return render_template('whos_that_pkmn_home.html')

# Route to initiate and handle gameplay interactions for the Who's That Pokémon game.
# It presents the game interface to the user and processes their input during the game.
@wtp_bp.route('/whos_that_pkmn', methods=['GET', 'POST'])
def start_game():
    # Retrieve the full database
    data_full = get_data_full()

    # Retrieve user game settings
    if request.method == 'POST':
        if 'gen' not in session:
            session['gen']  = request.form.getlist('gen[]')
        
        # If the game has ended, redirect to the score page
        result = game_end('wtp')
        if result:
            return result
    
    # Clean the session cache
    clean_session('reset_wtp')

    # Initialize the score count
    session['score'] = 0
    # Retrieve the user's high score, or initialize it as 0 if it's the user's first game
    session['high_score_wtp'] = session.get('high_score_wtp', 0)
    # Retrieve the list of already drawn Pokémon IDs; initialize as an empty list if none
    session['list_id'] = session.get('list_id', [])
    
    # Retrieve the list of generations selected by the user; default to all generations if none are selected
    generation = session.get('gen', all_generations)
    # Filter the database based on the generations selected by the user
    data = data_full.query('generation in @generation')

    # Draw Pokemon
    pkmn = sort_pkmn(data)

    # Retrieve the list of user correct answers; initialize as an empty list if none
    session['pkmn_list'] = session.get('pkmn_list', [])
    # Create a dictionary with the Pokémon's id-name, and the respective generation
    # This dictionary is used to record the user's answer history
    guessed_pkmn = guessed_pkmn = {
        "id_name": pkmn.id_name,
        "generation": data[data['id'] == pkmn.id]['generation_summary'].iloc[0]
    }
    session['pkmn_list'].append(guessed_pkmn)
    generations_dict = data.groupby('generation_summary')['id_name'].apply(list).to_dict()

    return render_template('whos_that_pkmn.html', pkmn=pkmn, generations_dict = generations_dict, high_score_wtp=session.get('high_score_wtp', 0))

@wtp_bp.route('/redraw_pokemons_wtp', methods=['GET', 'POST'])
def redraw_pokemons():
    # Retrieve the full database
    data_full = get_data_full()

    # Increase user score by 1
    session['score'] += 1

    # Variable to flag if the game ended
    game_end = 'False'

    # Retrieve the list of generations selected by the user; default to all generations if none are selected
    generation = session.get('gen', all_generations)
    # Filter the database based on the generations selected by the user
    data = data_full.query('generation in @generation')

    # Check if all Pokémons have been encountered to determine if the game has ended
    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        return jsonify({'game_end': game_end})

    # Draw new Pokemon
    new_pokemon = sort_pkmn(data)

    # Record user answer history
    guessed_pkmn = guessed_pkmn = {
        "id_name": new_pokemon.id_name,
        "generation": data[data['id'] == new_pokemon.id]['generation_summary'].iloc[0]
    }
    session['pkmn_list'].append(guessed_pkmn)

    return jsonify({
        'game_end': game_end,
        'id': new_pokemon.id,
        'name': new_pokemon.name,
        'id_name': new_pokemon.id_name,
        'sprite': new_pokemon.sprite,
        'shadow_sprite': new_pokemon.shadow_sprite
    })