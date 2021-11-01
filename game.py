import json
import os
import numpy as np

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
    
    def __init__(self, name):
        game = Game.all_games[name]
        self.name = game['name']
        self.name_ru = game.get('name_ru')
        if self.name_ru == None:
            self.name_ru = self.name
        self.board_width = game['board_width']
        self.board_length = game['board_length']
        self.board = [[None for y in range(self.board_length)] for x in range(self.board_width)]
        board = game['board'].split('/')
        for y in range(self.board_length):
            for x in range(self.board_width):
                if board[y][x] != '.':
                    piece = game['pieces'][board[y][x].lower()]
                    self.board[x][y] = {'piece': piece}
                    if board[y][x].isupper():
                        self.board[x][y]['isWhite'] = True
                    else:
                        self.board[x][y]['isWhite'] = False
                        
    def GetPieceMoves(self, x, y):
        legal_moves = []
        piece = self.board[x][y]
        if piece == None:
            return legal_moves
        coor = np.array([x, y])
        directions = {"N": np.array([0, -1]),
                      "S": np.array([0, 1]),
                      "W": np.array([-1, 0]),
                      "E": np.array([1, 0]) }
        if not piece['isWhite']:
            for d in directions.keys():
                directions[d] = -1*directions[d]
        # quite moves
        for move in piece['piece']['quite_moves']:
            new_coor = coor.copy()
            for d in move:
                new_coor += directions[d]
            if (0 <= new_coor[0] < self.board_width and
                0 <= new_coor[1] < self.board_length and
                self.board[new_coor[0]][new_coor[1]] is None):
                legal_moves.append(new_coor)
        # moves with capture
        for move in piece['piece']['quite_moves']:
            new_coor = coor.copy()
            for d in move:
                new_coor += directions[d]
            if (0 <= new_coor[0] < self.board_width and
                0 <= new_coor[1] < self.board_length and
                self.board[new_coor[0]][new_coor[1]] is not None and 
                self.board[new_coor[0]][new_coor[1]]['isWhite'] != piece['isWhite']):
                legal_moves.append(new_coor)
        return legal_moves

    def BoardTextOutput(self):
        Board = ''
        for y in range(self.board_width):
            for x in range(self.board_length):
                if self.board[x][y] == None:
                    Board += '.'
                elif self.board[x][y]['isWhite'] == False:
                    Board += self.board[x][y]['piece']['symbol']
                else:
                    Board += self.board[x][y]['piece']['symbol'].upper()
            Board += '\n'
        return Board