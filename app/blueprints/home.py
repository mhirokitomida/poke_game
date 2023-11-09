from flask import Blueprint, render_template
from ..utils import clean_session

# Blueprint for Home views and logic
home_bp = Blueprint('home', __name__)

# Serve the home page
# Also, clear any existing game session data to ensure a fresh start for the user.
@home_bp.route('/')
def index():
    clean_session('all')
    return render_template('index.html')