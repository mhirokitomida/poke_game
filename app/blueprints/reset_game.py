from flask import Blueprint, redirect, url_for, request
from ..utils import clean_session

# Blueprint for the game reset views and logic
reset_game_bp = Blueprint('reset_game', __name__)

# Route to reset the game state based on the specified game 
# Clears session data related to the game and redirects to the appropriate starting point.
@reset_game_bp.route('/reset_game', methods=['GET', 'POST'])
def reset_game():
     # Retrieve the type of reset requested from the form submission
    reset_type = request.form.get('reset_type')

    # Clear the session data specific to the requested reset type
    clean_session(reset_type)

    # Redirect to the appropriate game page based on the reset type:
    # - 'reset_hl' leads to the Higher Lower game page, preserving the current settings.
    # - 'reset_hl_all' leads to the Higher Lower home page, allowing the user to choose new settings.
    # - 'reset_wtp' leads to the Who's That Pokémon game page, preserving the current settings.
    # - 'reset_wtp_all' leads to the Who's That Pokémon home page, allowing the user to choose new settings.
    if reset_type == 'reset_hl':
        return redirect(url_for('higher_lower.start_game'))
    elif reset_type == 'reset_hl_all':
        return redirect(url_for('higher_lower.home'))
    elif reset_type == 'reset_wtp':
        return redirect(url_for('whos_that_pkmn.start_game'))
    elif reset_type == 'reset_wtp_all':
        return redirect(url_for('whos_that_pkmn.home'))