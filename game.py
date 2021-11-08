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
        self.pieces = game['pieces']
        self.isWhiteTurn = True
        self.numbers = [str(i+1) for i in range(self.board_length)]
        self.numbers.reverse()
        self.letters = [chr(ord('a')+i) for i in range(self.board_width)]
        
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
        for move in piece['piece'].get('quite_moves', []):
            new_coor = coor.copy()
            for d in move:
                new_coor += directions[d]
            if (0 <= new_coor[0] < self.board_width and
                0 <= new_coor[1] < self.board_length and
                self.board[new_coor[0]][new_coor[1]] is None):
                legal_moves.append(new_coor)
        # moves with capture
        for move in piece['piece'].get('capture_moves', []):
            new_coor = coor.copy()
            for d in move:
                new_coor += directions[d]
            if (0 <= new_coor[0] < self.board_width and
                0 <= new_coor[1] < self.board_length and
                self.board[new_coor[0]][new_coor[1]] is not None and 
                self.board[new_coor[0]][new_coor[1]]['isWhite'] != piece['isWhite']):
                legal_moves.append(new_coor)
        # slide quite moves
        for move in piece['piece'].get('slide_quite_moves', []):
            new_coor = coor.copy()
            shift = [0, 0]
            for d in move:
                shift += directions[d]
            new_coor += shift
            while (0 <= new_coor[0] < self.board_width and
                   0 <= new_coor[1] < self.board_length and
                   self.board[new_coor[0]][new_coor[1]] is None):
                legal_moves.append(new_coor.copy())
                new_coor += shift
        # slide moves with captures
        for move in piece['piece'].get('slide_capture_moves', []):
            new_coor = coor.copy()
            shift = [0, 0]
            for d in move:
                shift += directions[d]
            new_coor += shift
            while (0 <= new_coor[0] < self.board_width and
                   0 <= new_coor[1] < self.board_length):
                if self.board[new_coor[0]][new_coor[1]] is not None:
                    if self.board[new_coor[0]][new_coor[1]]['isWhite'] != piece['isWhite']:
                        legal_moves.append(new_coor.copy())
                    break 
                new_coor += shift
        for i in range(len(legal_moves)):
            legal_moves[i] = list(legal_moves[i])
        return legal_moves
    
    def PlayerMove(self, move):
        # TODO: check data correctness
        x = self.letters.index(move[0])
        y = self.numbers.index(move[1])
        x2 = self.letters.index(move[2])
        y2 = self.numbers.index(move[3])
        if self.board[x][y] is None:
            raise Exception('There is no piece on '+move[:2])
        if self.board[x][y]['isWhite'] != self.isWhiteTurn:
            raise Exception('It\'s not your turn')
        if [x2, y2] not in self.GetPieceMoves(x, y):
            raise Exception('Piece on '+move[:2]+' can\'t move on'+move[2:4])
        self.MovePiece(x, y, x2, y2)
        self.isWhiteTurn = not self.isWhiteTurn
    
    def MovePiece(self, x, y, x2, y2):
        piece = self.board[x][y]
        self.board[x][y] = None
        self.board[x2][y2] = piece
    
    def PlacePiece(self, x, y, piece, isWhite):
        piece = self.pieces[piece.lower()]
        self.board[x][y] = {'piece': piece}
        self.board[x][y]['isWhite'] = isWhite   
    
    def BoardTextOutput(self):
        Board = ''
        count = 8
        for y in range(self.board_width):
            for x in range(self.board_length):
                if self.board[x][y] == None:
                    Board += '.'
                elif self.board[x][y]['isWhite'] == False:
                    Board += self.board[x][y]['piece']['symbol']
                else:
                    Board += self.board[x][y]['piece']['symbol'].upper()
            Board += "|" + str(count)
            count -= 1
            Board += '\n'
        Board += "---------"
        Board += "\n"
        Board += "abcdefgh"
        return Board
    def BoardWithMovesTextOutpu(self, x, y):
        
        Board = self.BoardTextOutput()
        variants = self.GetPieceMoves(x, y)
        Board = Board.split("\n")
        length = len(Board)
        for new in range(length):
           Board[new] = list(Board[new]) 
        
        for l in variants:
            x = l[0]
            y = l[1]
            Board[y][x] = 'X'
            print(x)
            print(y)
        NewBoard = ""
        for i in range(10): 
            NewBoard += "".join(Board[i])
            NewBoard +="\n"
        return NewBoard