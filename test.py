from game import *
from piece import *


Piece.Load_all_pieces()
Game.Load_all_games()

print(Game.all_games)

a = Game('classic chess')

a.PlacePiece(4, 4, 'b', True)
print(a.GetPieceMoves(4, 4))

print(a.letters)
print(a.numbers)

a.PlayerMove('b1a3')
print(a.BoardTextOutput())
print(a.BoardWithMovesTextOutput(0, 6))

test_game = Game('classic chess')
while True:
    print(test_game.BoardTextOutput())
    test_game.PlayerMove(input())
    