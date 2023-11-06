from flask import Flask
import pandas as pd
from .config import Config
from .blueprints.home import home_bp
from .blueprints.higher_lower import higher_lower_bp
from .blueprints.whos_that_pkmn import wtp_bp
from .blueprints.reset_game import reset_game_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    data_full = pd.read_csv("https://raw.githubusercontent.com/mhirokitomida/poke_game/main/data/database/pokemon_database.csv", sep=",")
    data_full['id_name'] = data_full['id'].astype(str).str.zfill(3) + ' - ' + data_full['name']
    data_full['generation_summary'] = data_full['generation'].str.replace(r'generation-(\w+)', lambda m: 'Gen ' + m.group(1).upper(), regex=True)
    data_full['height'] = data_full['height'].astype(float) / 10
    data_full['weight'] = data_full['weight'].astype(float) / 10
    mapping = {
    'height': 'Height (cm)',
    'weight': 'Weight (Kg)',
    'hp': 'HP',
    'attack': 'Attack',
    'defense': 'Defense',
    'special-attack': 'Sp. Attack',
    'special-defense': 'Sp. Defense',
    'speed': 'Speed',
    'total': 'Total'
    }
    data_full.rename(columns=mapping, inplace=True)
    app.config['DATA_FULL'] = data_full

    app.register_blueprint(home_bp)
    app.register_blueprint(higher_lower_bp)
    app.register_blueprint(wtp_bp)
    app.register_blueprint(reset_game_bp)

    return app