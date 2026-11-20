import chess

from fiveaichess.utilities.utility import Utility


"""
An example of a utility function that provides a naive implementation
"""
class NewUtility(Utility):

    # calculates the amount of white pieces minus the amount of black pieces    
    def board_value(self, board: chess.Board):
        n_white = 0
        n_white += len(board.pieces(piece_type=chess.PAWN, color=chess.WHITE))
        n_white += len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE))*3
        n_white += len(board.pieces(piece_type=chess.KNIGHT, color=chess.WHITE))*3
        n_white += len(board.pieces(piece_type=chess.ROOK, color=chess.WHITE))*5
        n_white += len(board.pieces(piece_type=chess.QUEEN, color=chess.WHITE))*8

        n_black = 0
        n_black += len(board.pieces(piece_type=chess.PAWN, color=chess.BLACK))
        n_black += len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK))*3
        n_black += len(board.pieces(piece_type=chess.KNIGHT, color=chess.BLACK))*3
        n_black += len(board.pieces(piece_type=chess.ROOK, color=chess.BLACK))*5
        n_black += len(board.pieces(piece_type=chess.QUEEN, color=chess.BLACK))*8

        if board.is_checkmate():
            return -100000 if board.turn == chess.WHITE else 100000

        return n_white - n_black


