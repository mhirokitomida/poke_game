from flask import Blueprint, redirect, url_for, request
from ..utils import clean_session

reset_game_bp = Blueprint('reset_game', __name__)

@reset_game_bp.route('/reset_game', methods=['GET', 'POST'])
def reset_game():
    reset_type = request.form.get('reset_type')
    clean_session(reset_type)
    if reset_type == 'reset_hl':
        return redirect(url_for('higher_lower.start_game'))
    elif reset_type == 'reset_hl_all':
        return redirect(url_for('higher_lower.home'))
    elif reset_type == 'reset_wtp':
        return redirect(url_for('whos_that_pkmn.start_game'))
    elif reset_type == 'reset_wtp_all':
        return redirect(url_for('whos_that_pkmn.home'))