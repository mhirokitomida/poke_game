from flask import render_template, session, request, current_app 
import random
from .models import Pokemon
from .config import Config

# Retrieve all available generations and attributes 
# and Pokémon IDs with their respective generations from configuration (config.py)
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
    name = data[data['id'] == id_pkmn]['name'].iloc[0]
    stat_pkmn = data[data['id'] == id_pkmn][random_stat].iloc[0]
    sprite = data[data['id'] == id_pkmn]['url_sprite'].iloc[0]
    shadow_sprite = data[data['id'] == id_pkmn]['url_shadow_sprite'].iloc[0]
    id_name = data[data['id'] == id_pkmn]['id_name'].iloc[0]
    pkmn = Pokemon(id_pkmn, name, id_name, stat_pkmn, sprite, shadow_sprite)

    return pkmn

# Function used to convert Attribute to float or int
def transform_stat_number(stat, random_stat):
    return round(float(stat), 1) if random_stat in ['Height (cm)', 'Weight (Kg)'] else int(stat)

# Function to check if the game has ended and to redirect the user to the appropriate score page.
# It updates session variables for the high score and selects the correct score template based on the game type.
def game_end(game):
    # Set the high score session variable and choose the score template according to the game type
    if game == 'hl':
        high_score_game = 'high_score_hl'
        score_template = 'higher_lower_score.html'
        text_aux = "Pokémon Battles"
        num = 1
    elif game == 'wtp':
        high_score_game = 'high_score_wtp'
        score_template = 'whos_that_pkmn_score.html'
        text_aux = "Pokémons"
        num = 0

    # Retrieve the game end argument from the form submission
    game_end_arg = request.form.get('game_end_arg')

    # Proceed only if game_end_arg is provided
    if game_end_arg:
        # Retrieve the full database
        data_full = get_data_full()

        # Retrieve the list of generations selected by the user; default to all generations if none are selected
        generation = session.get('gen', all_generations)
        # Filter the database based on the generations selected by the user
        data = data_full.query('generation in @generation')
        max_rounds = len(data) - num

        # Update the session text to display on the score page based on the game's end condition
        # 'end' indicates the user made an incorrect guess
        # 'end_full' indicates the user guessed all Pokémon correctly
        if game_end_arg == 'end':
            session['pkmn_list'].pop() # Remove the last incorrect guess from the user's answer history
            session['text'] = f'You correctly got right {session["score"]} of {max_rounds} {text_aux} ({round((session["score"]/max_rounds)*100, 2)}%).'
            if session.get('score', 0) > session[high_score_game]:
                session[high_score_game] = max(session[high_score_game], session['score'])
                session['text'] = f'Congratulations, you have a new High Score: {session[high_score_game]} of {max_rounds} {text_aux} ({round((session["score"]/max_rounds)*100, 2)}%).'
                session['score_msg'] = ""
            else:
                session['score_msg'] = f'Your High score is {session[high_score_game]} {text_aux}.'
        elif game_end_arg == 'end_full':
            session[high_score_game] = max(session[high_score_game], session['score'])
            session['text'] = "Congratulations, you're a true Pokémon Master!"
            session['score_msg'] = f'You correctly got right all {(session["score"])} {text_aux}.'
        
        # Clear session text messages
        text = session.pop('text')
        score = session.pop('score_msg')

        # Get the user's correct answer list; use an empty list if none exist
        pkmn_list = session.get('pkmn_list', [])

        return render_template(score_template, text=text, score=score, pkmn_list=pkmn_list)
    
    return None

# Function to reset session variables to clear game state and user selections.
def clean_session(type = None):
    # Default keys to clear from the session for any game reset
    keys = ['score', 'text', 'score_msg', 'pkmn_list', 'list_id']

    # Specific keys to clear based on the game
    if type == 'reset_hl':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id'])
    elif type == 'reset_wtp':
        pass
    elif type == 'reset_hl_all' or 'all':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id', 'attributes', 'gen', 'data'])
    elif type == 'reset_wtp_all':
        keys.extend(['gen', 'data'])

    # Loop through the session and remove specified keys
    for key in list(session.keys()):
        if key in keys:
            session.pop(key, None)
        
    return(f'Cache Cleared: {type}')