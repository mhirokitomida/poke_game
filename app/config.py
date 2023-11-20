import os

class Config:
    SECRET_KEY = 'poke_game'
    GENERATIONS = [
        (1, 151, 'generation-i'),
        (152, 251, 'generation-ii'),
        (252, 386, 'generation-iii'),
        (387, 493, 'generation-iv'),
        (494, 649, 'generation-v'),
        (650, 721, 'generation-vi'),
        (722, 809, 'generation-vii'),
        (810, 898, 'generation-viii'),
        (899, 1025, 'generation-ix'),
    ]

    ALL_GENERATIONS = ['generation-i', 'generation-ii', 'generation-iii', 'generation-iv', 'generation-v', 'generation-vi', 'generation-vii', 'generation-viii']
    ALL_ATTRIBUTES = ['Height (cm)', 'Weight (Kg)', 'HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed', 'Total']

    DIR_PATH = os.path.dirname(os.path.abspath(__file__))