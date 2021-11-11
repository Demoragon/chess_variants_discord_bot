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
                    self.board[x][y]['MovedBefore'] = False
        self.pieces = game['pieces']
        self.game_flags = game['flags']
        self.isWhiteTurn = True
        self.en_passant = None
        self.numbers = [str(i+1) for i in range(self.board_length)]
        self.numbers.reverse()
        self.letters = [chr(ord('a')+i) for i in range(self.board_width)]
        
    def GetPieceMoves(self, x, y):
        legal_moves = []
        moves_info = dict()
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
        for move in piece['piece']['capture_moves']:
            new_coor = coor.copy()
            for d in move:
                new_coor += directions[d]
            if (0 <= new_coor[0] < self.board_width and
                0 <= new_coor[1] < self.board_length and
                self.board[new_coor[0]][new_coor[1]] is not None and 
                self.board[new_coor[0]][new_coor[1]]['isWhite'] != piece['isWhite']):
                legal_moves.append(new_coor)
        # slide quite moves
        for move in piece['piece']['slide_quite_moves']:
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
        for move in piece['piece']['slide_capture_moves']:
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
        # special moves
        # double move
        print(piece)
        if 'double_move' in piece['piece']['special_moves'] and not piece['MovedBefore']:
            # Make double_move more universal
            x2, y2 = directions['N']
            if self.board[x+x2][y+y2] is None and self.board[x+x2*2][y+y2*2] is None:
                new_move = [x+x2*2, y+y2*2]
                legal_moves.append(new_move)
                moves_info[str(new_move)] = "pawn_double_move"
        # en passant
        if 'en_passant' in piece['piece']['special_moves']:
            for move in piece['piece']['capture_moves']:
                new_coor = coor.copy()
                x2, y2 = directions['S']
                for d in move:
                    new_coor += directions[d]
                if (0 <= new_coor[0] < self.board_width and
                    0 <= new_coor[1] < self.board_length and
                    self.en_passant == [new_coor[0]+x2,new_coor[1]+y2]):
                    legal_moves.append(new_coor)
                    moves_info[str(list(new_coor))] = 'en_passant'
        # castling
        if ('castling' in self.game_flags and 
            'king' in piece['piece']['flags'] and not piece['MovedBefore']):
            # TODO: check if castling is actually legal
            if self.board[0][y] is not None and not self.board[0][y]['MovedBefore']:
                legal_moves.append([x-2, y])
                moves_info[str([x-2, y])] = 'long_castling'
            if (self.board[self.board_width-1][y] is not None and 
                not self.board[self.board_width-1][y]['MovedBefore']):
                legal_moves.append([x+2, y])
                moves_info[str([x+2, y])] = 'short_castling'            
        for i in range(len(legal_moves)):
            legal_moves[i] = list(legal_moves[i])
        return legal_moves, moves_info
    
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
        legal_moves, moves_info = self.GetPieceMoves(x, y)
        if [x2, y2] not in legal_moves:
            raise Exception(self.board[x][y]['piece']['name']+
                            ' on '+move[:2]+' can\'t move on '+move[2:4])
        self.MovePiece(x, y, x2, y2)
        if moves_info.get(str([x2, y2]), None) == "en_passant":
            x3, y3 = self.en_passant
            self.board[x3][y3] = None
        if moves_info.get(str([x2, y2]), None) == "long_castling":
            self.MovePiece(0, y, x2+1, y2)
        if moves_info.get(str([x2, y2]), None) == "short_castling":
            # TODO: list of pieces which this one can transform into
            # TODO: check correctness of data connected with transformation
            self.MovePiece(self.board_width-1, y, x2-1, y2)
        if ('pawn' in self.board[x2][y2]['piece']['flags'] and
            ((self.board[x2][y2]['isWhite'] and y2 == 0) or
             (not self.board[x2][y2]['isWhite'] and y2 == self.board_length-1))):
            self.board[x2][y2]['piece'] = self.pieces[move[4].lower()]
        if moves_info.get(str([x2, y2]), None) == "pawn_double_move":
            self.en_passant = [x2, y2]
        else:
            self.en_passant = None
        
        self.isWhiteTurn = not self.isWhiteTurn
        self.board[x2][y2]['MovedBefore'] = True
    
    def MovePiece(self, x, y, x2, y2):
        piece = self.board[x][y]
        self.board[x][y] = None
        self.board[x2][y2] = piece
    
    def PlacePiece(self, x, y, piece, isWhite):
        piece = self.pieces[piece.lower()]
        self.board[x][y] = {'piece': piece}
        self.board[x][y]['isWhite'] = isWhite
        self.board[x][y]['MovedBefore'] = False
    
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
      
    def BoardWithMovesTextOutput(self, x, y):
        Board = self.BoardTextOutput()
        variants, _ = self.GetPieceMoves(x, y)
        Board = Board.split("\n")
        length = len(Board)
        for new in range(length):
            Board[new] = list(Board[new]) 
        
        for v in variants:
            x, y = v
            Board[y][x] = 'X'
        NewBoard = ""
        for i in range(10): 
            NewBoard += "".join(Board[i])
            NewBoard +="\n"
        return NewBoard
