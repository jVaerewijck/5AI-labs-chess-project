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

    def calculate_move(self, board: Board, constraints: dict[str, int] = {}) -> Move:
        start_time = time.time()
        
        best_move = random.sample(list(board.legal_moves), 1)[0]
        best_utility = float("-inf")

        alpha = float("-inf")
        beta = float("inf")

        # loop trough all legal moves
        for move in self.order_moves(board, self.depth):

            # check if the maximum calculation time for this move has been reached
            # if time.time() - start_time > self.time_limit_move:
            #     break
            
            # play the move
            board.push(move)

            # determine the value of the board after this move
            value = -self.negamax(board,
            self.depth - 1,
            -alpha,
            -beta,
            start_time
            )

            # if this is better than all other previous moves, store this move and its utility
            if value > alpha :
                best_move = move
                alpha  = value

            # revert the board to its original state
            board.pop()

        return best_move

    def evaluate(self, board: Board) -> float:
        v = self.utility.board_value(board)
        return v if board.turn == chess.WHITE else -v
    
    def negamax(self, board: Board, depth: int, alpha: float, beta: float, start_time: float, constraints: dict[str, int] = {}) -> float:
        if board.is_game_over():
            return self.evaluate(board)
        if depth == 0:
            return self.quiescence(board, alpha, beta)
        # if time.time() - start_time > self.time_limit_move:
        #     raise TimeoutError

        best = float("-inf")

        for move in self.order_moves(board, depth):
            board.push(move)
            value = -self.negamax(board, depth - 1, -beta, -alpha, start_time)
            board.pop()

            if value > best:
                best = value
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best

    def quiescence(self, board: Board, alpha: float, beta: float, qdepth: int = 8) -> float:
        stand_pat = self.evaluate(board)
        if qdepth == 0 or stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)
        best = stand_pat

        for move in self.order_captures(board):
            board.push(move)
            value = -self.quiescence(board, -beta, -alpha, qdepth - 1)
            board.pop()

            best = max(best, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best
    
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

    def order_moves(self, board: Board,depth: int) -> list[Move]:
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
            return sorted(board.legal_moves, key=score, reverse=True)
        else:
            return list(board.legal_moves)
