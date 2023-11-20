from flask import Blueprint, render_template, session, request, jsonify
import random
from ..models import Pokemon
from ..utils import get_data_full, get_all_generations, get_all_attributes, sort_pkmn, transform_stat_number, game_end, clean_session

# Blueprint for the Higher-Lower game views and logic
higher_lower_bp = Blueprint('higher_lower', __name__, template_folder='../templates')

# Retrieve all available generations and attributes from configuration (config.py)
all_generations = get_all_generations()
all_attributes = get_all_attributes()

# Serve the home page for the Higher Lower game, which includes instructions and settings.
# Also, clear any existing game session data to ensure a fresh start for the user.
@higher_lower_bp.route('/higher_lower_home', methods=['GET', 'POST'])
def home():
    clean_session('all')
    return render_template('higher_lower_home.html')

# Route to initiate and handle gameplay interactions for the Higher Lower game.
# It presents the game interface to the user and processes their input during the game.
@higher_lower_bp.route('/higher_lower', methods=['GET', 'POST'])
def start_game():
    # Retrieve the full database
    data_full = get_data_full()

    # Retrieve user game settings
    if request.method == 'POST':
        if 'gen' not in session and 'attributes' not in session:
            session['gen']  = request.form.getlist('gen[]')
            session['attributes'] = request.form.getlist('attributes[]')

        # If the game has ended, redirect to the score page
        result = game_end('hl')
        if result:
            return result

    # Clean the session cache
    clean_session('reset_hl')

    # Initialize the score count
    session['score'] = 0
    # Retrieve the user's high score, or initialize it as 0 if it's the user's first game
    session['high_score_hl'] = session.get('high_score_hl', 0)
    # Retrieve the list of already drawn Pokémon IDs; initialize as an empty list if none
    session['list_id'] = session.get('list_id', [])
    
    # Retrieve the list of attributes selected by the user; default to all attributes if none are selected
    stats = session.get('attributes', all_attributes)
    # Choose a random stat from the list of stats
    random_stat = random.choice(stats)

    # Retrieve the list of generations selected by the user; default to all generations if none are selected
    generation = session.get('gen', all_generations)
    # Filter the database based on the generations selected by the user
    data = data_full.query('generation in @generation')

    # Draw Pokemon 1
    pkmn_1 = sort_pkmn(data, random_stat)
    # Draw Pokemon 2
    pkmn_2 = sort_pkmn(data, random_stat)

    # Save in session cache the last Pokemon 1 and 2 ID's
    session['last_pkmn_1_id'] = pkmn_1.id
    session['last_pkmn_2_id'] = pkmn_2.id

    # Retrieve the list of user correct answers; initialize as an empty list if none
    session['pkmn_list'] = session.get('pkmn_list', [])
    # Create a dictionary with a random stat, the Pokémon's name, and the respective stat value
    # This dictionary is used to record the user's answer history
    battle = battle = {
        "stat": random_stat,
        "name1": pkmn_1.name,
        "stat1": transform_stat_number(pkmn_1.stat, random_stat), 
        "name2": pkmn_2.name,
        "stat2": transform_stat_number(pkmn_2.stat, random_stat)
    }
    session['pkmn_list'].append(battle)

    return render_template('higher_lower.html', stat=random_stat, pkmn_1=pkmn_1, pkmn_2=pkmn_2, high_score_hl=session.get('high_score_hl', 0))

# Redraw Pokemon after a correct answer
@higher_lower_bp.route('/redraw_pokemons_hl', methods=['GET', 'POST'])
def redraw_pokemons():
    # Retrieve the full database
    data_full = get_data_full()

    # Increase user score by 1
    session['score'] += 1

    # Variable to flag if the game ended
    game_end = 'False'

    # Get the ID of last selected Pokemon
    last_id = request.args.get('last_id')

    # Retrieve the list of attributes selected by the user; default to all attributes if none are selected
    stats = session.get('attributes', all_attributes)
    # Choose a random stat from the list of stats
    random_stat = random.choice(stats)

    # Retrieve the list of generations selected by the user; default to all generations if none are selected
    generation = session.get('gen', all_generations)
    # Filter the database based on the generations selected by the user
    data = data_full.query('generation in @generation')

    # Check if all Pokémons have been encountered to determine if the game has ended
    if len(session.get('list_id', [])) == len(data):
        game_end = 'True'
        return jsonify({
        'game_end': game_end
        })

    # Draw new Pokemon
    new_pokemon = sort_pkmn(data, random_stat)

    # Determine which previously selected Pokémon to replace with the new one
    if last_id == 'pkmn-1':
        id_pkmn_old = session['last_pkmn_1_id']
        session['last_pkmn_2_id'] = new_pokemon.id
    else:
        id_pkmn_old = session['last_pkmn_2_id']
        session['last_pkmn_1_id'] = new_pokemon.id

    # Retrieve details of the previously selected Pokémon based on its ID
    old_name = data[data['id'] == id_pkmn_old]['name'].iloc[0]
    old_id_name = data[data['id'] == id_pkmn_old]['id_name'].iloc[0]
    stat_pkmn_old = data[data['id'] == id_pkmn_old][random_stat].iloc[0]
    sprite_old = data[data['id'] == id_pkmn_old]['url_sprite'].iloc[0]
    old_pokemon = Pokemon(id_pkmn_old, old_name, old_id_name, stat_pkmn_old, sprite_old)

    # Record user answer history based on last selected Pokémon
    if last_id == 'pkmn-1':
        battle = {
        "stat": random_stat,
        "name1": old_pokemon.name,
        "stat1": transform_stat_number(old_pokemon.stat, random_stat),
        "name2": new_pokemon.name,
        "stat2": transform_stat_number(new_pokemon.stat, random_stat)
        }
    else:
        battle = {
        "stat": random_stat,
        "name1": new_pokemon.name,
        "stat1": transform_stat_number(new_pokemon.stat, random_stat),
        "name2": old_pokemon.name,
        "stat2": transform_stat_number(old_pokemon.stat, random_stat)
        }
    session['pkmn_list'].append(battle)

    # Return the game status, the newly drawn stat, the new Pokémon details, 
    # and the details of the Pokémon to be retained
    return jsonify({
        'game_end': game_end,
        'random_stat': random_stat,
        'new_pokemon': {
            'id': new_pokemon.id,
            'name': new_pokemon.name,
            'stat': transform_stat_number(new_pokemon.stat, random_stat),
            'sprite': new_pokemon.sprite
        },
        'old_pokemon': {
            'id': old_pokemon.id,
            'name': old_pokemon.name,
            'stat': transform_stat_number(old_pokemon.stat, random_stat),
            'sprite': old_pokemon.sprite
        }
    })