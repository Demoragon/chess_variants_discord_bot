from game import *
from piece import *


Piece.Load_all_pieces()
Game.Load_all_games()

print(Game.all_games)

a = Game('classic chess')

a.PlacePiece(4, 4, 'b', True)
print(a.GetPieceMoves(4, 4))
