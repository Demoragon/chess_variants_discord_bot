import json
import os


class Piece:
    all_pieces = dict()
    
    @staticmethod
    def Load_all_pieces():
        for file_name in os.listdir('pieces/'):
            with open('pieces/'+file_name, 'r') as file:
                for piece_json in json.load(file):
                    Piece.all_pieces[piece_json['name']] = Piece.Get_piece_from_json(piece_json)        
    
    @staticmethod
    def Get_piece_from_json(json_piece):
        # TODO: check data correctness
        keys = json_piece.keys()
        move_types = [ "quite_moves", "capture_moves",
                       "slide_quite_moves", "slide_capture_moves",
                       "special_moves", "flags" ]
        for move_type in move_types:
            if move_type not in keys:
                json_piece[move_type] = []
        return json_piece     
        