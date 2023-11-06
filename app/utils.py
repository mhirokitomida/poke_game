from flask import render_template, session, request, current_app 
import random
from .models import Pokemon
from .config import Config

generations = Config.GENERATIONS
all_generations = Config.ALL_GENERATIONS
all_attributes = Config.ALL_ATTRIBUTES

# Get full database
def get_data_full():
    with current_app.app_context():
        return current_app.config['DATA_FULL']

# Get Dict with Generations and Pokemon ID range
def get_generations():
    return Config.GENERATIONS

# Get all Generations
def get_all_generations():
    return Config.ALL_GENERATIONS

# Get all attributes
def get_all_attributes():
    return Config.ALL_ATTRIBUTES

# Draw a random number in available Pokemon ID
def randint_exclude(gens, exclude):
    # Filters the number ranges of the specified generations
    gen_ranges = [(start, end) for start, end, gen in generations if gen in gens]

    # Combines all the ranges into a list of permitted numbers
    allowed_numbers = []
    for start, end in gen_ranges:
        allowed_numbers.extend(range(start, end + 1))
    
    # Filters the permitted numbers by excluding those on the exclusion list
    allowed_numbers = [num for num in allowed_numbers if num not in exclude] 

    if not allowed_numbers:
        raise ValueError("No numbers available with the given constraints.")

    # Draws a random number from the permitted numbers
    return random.choice(allowed_numbers)

# Create Pokemon object using randint_exclude() function
def sort_pkmn(data, random_stat = all_attributes):
    # Draw a random Pokemon ID
    id_pkmn = randint_exclude(session.get('gen', []), session.get('list_id', []))
    # Put ID in the exclusion list
    session['list_id'].append(id_pkmn)
    session['list_id'] = list(set(session['list_id']))

    # Create Pokemon object
    nome = data.loc[id_pkmn, 'name']
    stat_pkmn = data.loc[id_pkmn, random_stat]
    sprite = data.loc[id_pkmn, 'url_sprite']
    shadow_sprite = data.loc[id_pkmn, 'url_shadow_sprite']
    id_name = data.loc[id_pkmn, 'id_name']
    pkmn = Pokemon(id_pkmn, nome, id_name, stat_pkmn, sprite, shadow_sprite)

    return pkmn

# Function used to convert Attribute to float or int
def transform_stat_number(stat, random_stat):
    return round(float(stat), 1) if random_stat in ['Height (cm)', 'Weight (Kg)'] else int(stat)

# Function to verify and redirect when game ended
def game_end(game):
    if game == 'hl':
        high_score_game = 'high_score_hl'
        score_template = 'higher_lower_score.html'
    elif game == 'wtp':
        high_score_game = 'high_score_wtp'
        score_template = 'whos_that_pkmn_score.html'

    game_end_arg = request.form.get('game_end_arg')
    if game_end_arg:
        data_full = get_data_full()
        generation = session.get('gen', all_generations)
        data = data_full.query('generation in @generation')
        if game_end_arg == 'end':
            session['text'] = f'You correctly got right {session["score"]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
            if session.get('score', 0) > session[high_score_game]:
                session[high_score_game] = max(session[high_score_game], session['score'])
                session['text'] = f'Congratulations, you have a new High Score: {session[high_score_game]} of {len(data)} Pokémons ({round((session["score"]/len(data))*100, 2)}%).'
                session['score_msg'] = ""
            else:
                session['score_msg'] = f'Your High score is {session[high_score_game]} Pokémons.'
        elif game_end_arg == 'end_full':
            session[high_score_game] = max(session[high_score_game], session['score'])
            session['text'] = "Congratulations, you're a true Pokémon Master!"
            session['score_msg'] = f'You correctly got right all {len(session["list_id"])} Pokémons.'
        
        session['pkmn_list'].pop()
        text = session.pop('text')
        score = session.pop('score_msg')
        pkmn_list = session.get('pkmn_list', [])
        return render_template(score_template, text=text, score=score, pkmn_list=pkmn_list)
    
    return None

# Function to clear specific parameters in session cache
def clean_session(type = None):
    keys = ['score', 'text', 'score_msg', 'pkmn_list', 'list_id']
    if type == 'reset_hl':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id'])
    elif type == 'reset_wtp':
        pass
    elif type == 'reset_hl_all' or 'all':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id', 'attributes', 'gen', 'data'])
    elif type == 'reset_wtp_all':
        keys.extend(['gen', 'data'])

    for key in list(session.keys()):
        if key in keys:
            session.pop(key, None)
        
    return(f'Cache Cleared: {type}')