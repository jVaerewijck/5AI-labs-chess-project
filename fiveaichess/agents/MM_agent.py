import time
import random

import chess

from chess import Board, Move

from fiveaichess.agents.agent import Agent
from fiveaichess.utilities.utility import Utility


"""
An example of a chess agent that provides a naive implementation

This agent iterates trough all the moves possible and picks the one with the highest utility.

"""
class MMAgent(Agent):

    name = "NewChessAgent"

    author = "Jarn&Loïc"

    

    def __init__(self, utility: Utility, time_limit_move: float, depth: int = 5):
        super().__init__(utility, time_limit_move)
        # initialize your agent with additional parameters if needed
        self.PIECE_VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
                        chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
        self.depth = depth
        self.tt = {} #transposition table
        self.EXACT, self.LOWER, self.UPPER = 0, 1, 2

    def calculate_move(self, board: Board, constraints: dict[str, int] = {}) -> Move:
        start_time = time.time()
        
        best_move = random.sample(list(board.legal_moves), 1)[0]

        alpha, beta = float("-inf"), float("inf")

        entry = self.tt.get(board._transposition_key())
        tt_move = entry[3] if entry else None

        # loop trough all legal moves
        for move in self.order_moves(board, self.depth,tt_move):

            # check if the maximum calculation time for this move has been reached
            # if time.time() - start_time > self.time_limit_move:
            #     break
            
            # play the move
            board.push(move)

            # determine the value of the board after this move
            value = -self.negamax(board,
            self.depth - 1,
            -beta,
            -alpha,
            start_time
            )

            # if this is better than all other previous moves, store this move and its utility
            if value > alpha :
                best_move = move
                alpha  = value

            # revert the board to its original state
            board.pop()

        self.tt[board._transposition_key()] = (self.depth, alpha, self.EXACT, best_move)

        return best_move

    def evaluate(self, board: Board, ply: int) -> float:
        v = self.utility.board_value(board)   #add ply
        return v if board.turn == chess.WHITE else -v
    
    def negamax(self, board: Board, depth: int, alpha: float, beta: float, start_time: float, ply: int = 0, constraints: dict[str, int] = {}) -> float:
        if board.is_game_over():
            return self.evaluate(board, ply)
        # if board.is_game_over():          # stalemate, repetition, 50-move, insufficient material
        #     return 0
        if board.is_repetition(2):
            return 0
        if depth == 0:
            return self.quiescence(board, alpha, beta, ply)
        # if time.time() - start_time > self.time_limit_move:
        #     raise TimeoutError

        
        key = board._transposition_key()
        alpha_orig = alpha
        tt_move = None

        entry = self.tt.get(key)
        if entry:
            e_depth, e_score, e_flag, e_move = entry
            tt_move = e_move
            if e_depth >= depth:
                if e_flag == self.EXACT:
                    return e_score
                elif e_flag == self.LOWER:
                    alpha = max(alpha, e_score)
                else:  # UPPER
                    beta = min(beta, e_score)
                if alpha >= beta:
                    return e_score

        best = float("-inf")
        best_move = None

        for move in self.order_moves(board, depth, tt_move):
            board.push(move)
            value = -self.negamax(board, depth - 1, -beta, -alpha, start_time, ply +1)
            board.pop()

            if value > best:
                best = value
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        if best <= alpha_orig:
            flag = self.UPPER
        elif best >= beta:
            flag = self.LOWER
        else:
            flag = self.EXACT
        if len(self.tt) >= 1_000_000:
            for k in list(self.tt)[:1_000_000 // 4]:
                del self.tt[k]
        self.tt[key] = (depth, best, flag, best_move)

        return best

    def quiescence(self, board: Board, alpha: float, beta: float, ply: int, qdepth: int = 8) -> float:
        if board.is_check() and board.is_checkmate():
            return -100000 + ply
        stand_pat = self.evaluate(board,ply)
        if qdepth == 0 or stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)
        best = stand_pat

        for move in self.order_captures(board):
            board.push(move)
            value = -self.quiescence(board, -beta, -alpha, ply + 1, qdepth - 1)
            board.pop()

            best = max(best, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best

    def order_captures(self, board: Board) -> list[Move]:
        def score(move: Move) -> int:
            s = 0
            if board.is_capture(move):
                victim = chess.PAWN if board.is_en_passant(move) else board.piece_type_at(move.to_square)
                attacker = board.piece_type_at(move.from_square)
                s += 10000 + 10 * self.PIECE_VALUES[victim] - self.PIECE_VALUES[attacker]
            if move.promotion:
                s += 9000 + self.PIECE_VALUES[move.promotion]
            return s

        moves = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
        moves.sort(key=score, reverse=True)
        return moves
    
    def minimax(self, board: Board, depth: int, maximizing: bool , flip_value: int, alpha: float, beta: float, start_time: float, constraints: dict[str, int] = {}):
        if depth == 0 or board.is_game_over():
             return flip_value * self.utility.board_value(board)

        # if time.time() - start_time > self.time_limit_move:
        #     raise TimeoutError

        if maximizing:

            max_eval = float("-inf")

            for move in board.legal_moves:

                board.push(move)

                evaluation = self.minimax(
                    board,
                    depth - 1,
                    False,
                    flip_value,
                    alpha,
                    beta,
                    start_time
                )

                board.pop()

                max_eval = max(max_eval, evaluation)

                # Alpha-beta pruning
                alpha = max(alpha, evaluation)

                if beta <= alpha:
                    break

            return max_eval

        else:

            min_eval = float("inf")

            for move in board.legal_moves:

                board.push(move)

                evaluation = self.minimax(
                    board,
                    depth - 1,
                    True,
                    flip_value,
                    alpha,
                    beta,
                    start_time
                )

                board.pop()

                min_eval = min(min_eval, evaluation)

                beta = min(beta, evaluation)

                # Alpha-beta pruning
                if beta <= alpha:
                    break

            return min_eval

    def order_moves(self, board: Board,depth: int, tt_move=None) -> list[Move]:
        def score(move: Move) -> int:
            s = 0

            if board.is_capture(move):
                victim = chess.PAWN if board.is_en_passant(move) else board.piece_type_at(move.to_square)
                attacker = board.piece_type_at(move.from_square)
                # big victim, small attacker => high score; +10000 keeps captures above quiet moves
                s += 10000 + 10 * self.PIECE_VALUES[victim] - self.PIECE_VALUES[attacker]

            if move.promotion:
                s += 9000 + self.PIECE_VALUES[move.promotion]

            if board.gives_check(move) and depth <=5:
                s += 500

            return s
        if depth >= 2:
            moves = sorted(board.legal_moves, key=score, reverse=True)
        else:
            moves = list(board.legal_moves)
        if tt_move is not None and tt_move in board.legal_moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)
        return moves
