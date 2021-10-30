import json
import os

from piece import *

class Game:
    all_games = dict()
    
    @staticmethod
    def Load_all_games():
        for file_name in os.listdir('games/'):
            with open('games/'+file_name, 'r') as file:
                for game_json in json.load(file):
                    Game.all_games[game_json['name']] = Game.Get_game_from_json(game_json)        

    @staticmethod
    def Get_game_from_json(json_game):
        # TODO: check data correctness
        new_game = json_game
        for piece in new_game['pieces'].keys():
            new_game['pieces'][piece] = Piece.all_pieces[new_game['pieces'][piece]]
        return json_game
        