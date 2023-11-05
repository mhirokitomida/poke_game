from flask import render_template, session, request, current_app 
import random
from .models import Pokemon
from .config import Config

generations = Config.GENERATIONS
all_generations = Config.ALL_GENERATIONS
all_stats = Config.ALL_STATS

def get_data_full():
    with current_app.app_context():
        return current_app.config['DATA_FULL']

def get_generations():
    # Access the config within an application context
    return Config.GENERATIONS

def get_all_generations():
    # Access the config within an application context
    return Config.ALL_GENERATIONS

def get_all_stats():
    # Access the config within an application context
    return Config.ALL_STATS

def randint_exclude(gens, exclude):
    
    # Filtra os intervalos de números das gerações especificadas
    gen_ranges = [(start, end) for start, end, gen in generations if gen in gens]

    # Junta todos os intervalos em uma lista de números permitidos
    allowed_numbers = []
    for start, end in gen_ranges:
        allowed_numbers.extend(range(start, end + 1))
    
    # Filtra os números permitidos excluindo os da lista de exclusão
    allowed_numbers = [num for num in allowed_numbers if num not in exclude]

    if not allowed_numbers:
        raise ValueError("No numbers available with the given constraints.")

    # Sorteia um número aleatório dos números permitidos
    return random.choice(allowed_numbers)

def sort_pkmn(data, random_stat = all_stats):
    id_pkmn = randint_exclude(session.get('gen', []), session.get('list_id', []))
    session['list_id'].append(id_pkmn)
    session['list_id'] = list(set(session['list_id']))
    nome = data.loc[id_pkmn, 'name']
    stat_pkmn = data.loc[id_pkmn, random_stat]
    sprite = data.loc[id_pkmn, 'url_sprite']
    shadow_sprite = data.loc[id_pkmn, 'url_shadow_sprite']
    pkmn = Pokemon(id_pkmn, nome, stat_pkmn, sprite, shadow_sprite)

    return pkmn

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

def clean_session(type = None):
    keys = ['score', 'text', 'score_msg', 'pkmn_list', 'list_id']
    if type == 'reset_hl':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id'])
    elif type == 'reset_wtp':
        pass
    elif type == 'reset_hl_all' or 'all':
        keys.extend(['last_pkmn_1_id', 'last_pkmn_2_id', 'atributes', 'gen', 'data'])
    elif type == 'reset_wtp_all':
        keys.extend(['gen', 'data'])

    for key in list(session.keys()):
        if key in keys:
            session.pop(key, None)
        
    return(f'Cacher Cleared: {type}')