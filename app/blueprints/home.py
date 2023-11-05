from flask import Blueprint, render_template
from ..utils import sort_pkmn, clean_session, game_end

# Definir o Blueprint 'home'
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    clean_session('all')
    return render_template('index.html')