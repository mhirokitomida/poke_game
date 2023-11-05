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
    app.config['DATA_FULL'] = data_full

    app.register_blueprint(home_bp)
    app.register_blueprint(higher_lower_bp)
    app.register_blueprint(wtp_bp)
    app.register_blueprint(reset_game_bp)

    return app