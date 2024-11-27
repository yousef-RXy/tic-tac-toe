import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import threading
import math
import copy
import time
from enum import Enum


def print_board(current_board):
    with lock:
        print("Current board:")
        for i in range(3):
            print(
                f"{current_board[i][0]} | {current_board[i][1]} | {current_board[i][2]}"
            )
            print("--+---+---")

        winner = check_winner(current_board)
        if winner:
            print("Winner is: " + winner)
        elif is_full(board):
            print("Tie")

        print()


def minimax(depth, is_maximizing, max_depth=math.inf, heuristic=None):
    global PLAYER_O, PLAYER_X, board, called
    called += 1

    # current_board = copy.deepcopy(board)
    # printer.submit(lambda: print_board(current_board))

    winner = check_winner(board)
    if winner == PLAYER_X:
        return 10 - depth
    elif winner == PLAYER_O:
        return depth - 10
    elif is_full(board):
        return 0

    if depth >= max_depth:
        return heuristic()

    if is_maximizing:
        max_eval = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_X
                    eval = minimax(depth + 1, False, max_depth, heuristic)
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_O
                    eval = minimax(depth + 1, True, max_depth, heuristic)
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
        return min_eval


def minimax_with_alpha_beta(depth, is_maximizing, alpha, beta):
    global PLAYER_O, PLAYER_X, board, called

    called += 1
    # current_board = copy.deepcopy(board)
    # printer.submit(lambda: print_board(current_board))

    winner = check_winner(board)
    if winner == PLAYER_X:
        return 10 - depth
    elif winner == PLAYER_O:
        return depth - 10
    elif is_full(board):
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_X
                    eval = minimax_with_alpha_beta(depth + 1, False, alpha, beta)
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
                    if eval >= beta:
                        return beta
                    alpha = max(alpha, eval)
        return max_eval
    else:
        min_eval = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_O
                    eval = minimax_with_alpha_beta(depth + 1, True, alpha, beta)
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
                    if eval <= alpha:
                        return alpha
                    beta = min(beta, eval)
        return min_eval


def check_winning_lines_heuristic():
    global PLAYER_O, PLAYER_X, board

    score = 0
    winning_lines = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    for line in winning_lines:
        ai_count = 0
        opponent_count = 0

        for row, col in line:
            if board[row][col] == PLAYER_X:
                ai_count += 1
            elif board[row][col] == PLAYER_O:
                opponent_count += 1

        if ai_count == 3:
            return 1000
        elif opponent_count == 3:
            return -1000
        elif ai_count == 2 and opponent_count == 0:
            score += 10
        elif opponent_count == 2 and ai_count == 0:
            score -= 10

    return score


def center_control_heuristic():
    global PLAYER_O, PLAYER_X, board

    score = 0
    if board[1][1] == PLAYER_X:
        score += 10
    elif board[1][1] == PLAYER_O:
        score -= 10

    return score


def corners_control_heuristic():
    global PLAYER_O, PLAYER_X, board

    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]

    score = 0

    for corner in corners:
        if board[corner[0]][corner[1]] == PLAYER_X:
            score += 5
        elif board[corner[0]][corner[1]] == PLAYER_O:
            score -= 5

    return score


def combined_heuristic():
    return (
        check_winning_lines_heuristic()
        + center_control_heuristic() * 0.3
        + corners_control_heuristic()
    )


def ai_move():
    global board, buttons, PLAYER_X, called, current_game_mode

    start_time = time.time()
    best_val = -math.inf
    ai_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = PLAYER_X

                if current_game_mode == GameModes.MINIMAX:
                    move_val = minimax(0, False)
                elif current_game_mode == GameModes.ALPHA_BETA:
                    move_val = minimax_with_alpha_beta(0, False, -math.inf, math.inf)
                elif current_game_mode == GameModes.HEURISTIC_1:
                    move_val = minimax(0, False, 4, check_winning_lines_heuristic)
                elif current_game_mode == GameModes.HEURISTIC_2:
                    move_val = minimax(0, False, 3, combined_heuristic)

                board[i][j] = " "
                if move_val > best_val:
                    best_val = move_val
                    ai_move = (i, j)

    print(time.time() - start_time)
    print(called)
    called = 0
    board[ai_move[0]][ai_move[1]] = PLAYER_X
    buttons[ai_move[0]][ai_move[1]].config(text=PLAYER_X)
    toggle_buttons(True)
    check_game_status()


def is_full(board):
    return all(cell != " " for row in board for cell in row)


def check_winner(board):
    winning_combinations = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    for combination in winning_combinations:
        if (
            board[combination[0][0]][combination[0][1]]
            == board[combination[1][0]][combination[1][1]]
            == board[combination[2][0]][combination[2][1]]
            != " "
        ):
            return board[combination[0][0]][combination[0][1]]


def check_game_status():
    global game_over
    winner = check_winner(board)
    if winner:
        game_over = True
        messagebox.showinfo("Game Over", f"{winner} wins!")
        return True
    elif is_full(board):
        game_over = True
        messagebox.showinfo("Game Over", "It's a draw!")
        return True
    return False


def button_click(row, col):
    global board, buttons
    if board[row][col] == " " and not game_over:
        board[row][col] = PLAYER_O
        buttons[row][col].config(text=PLAYER_O, state=tk.DISABLED)
        if check_game_status():
            return

        toggle_buttons(False)

        executor.submit(ai_move)


def toggle_buttons(enable):
    global buttons
    state = tk.NORMAL if enable else tk.DISABLED
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                buttons[i][j].config(state=state)


def reset_game():
    global board, game_over
    board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    game_over = False
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", state=tk.NORMAL)


def set_game_mode(selected_mode):
    global current_game_mode
    current_game_mode = selected_mode
    reset_game()
    for button, mode in mode_buttons.items():
        if mode == selected_mode:
            button.config(relief=tk.SUNKEN, state=tk.DISABLED)
        else:
            button.config(relief=tk.RAISED, state=tk.NORMAL)
    print(f"Game mode set to: {selected_mode}")


class GameModes(Enum):
    MINIMAX = 0
    ALPHA_BETA = 1
    HEURISTIC_1 = 2
    HEURISTIC_2 = 3
    ALPHA_BET4 = 4
    ALPHA_BET5 = 5


PLAYER_X = "X"
PLAYER_O = "O"
current_game_mode = GameModes.MINIMAX
called = 0
mode_buttons = {}
game_over = False
board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
buttons = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
executor = ThreadPoolExecutor(max_workers=1)
printer = ThreadPoolExecutor()
lock = threading.Lock()

root = tk.Tk()
root.title("Tic-Tac-Toe")

for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(
            root,
            text="",
            font=("Arial", 24),
            height=2,
            width=5,
            command=lambda row=i, col=j: button_click(row, col),
        )
        buttons[i][j].grid(row=i, column=j + 1)

for game_mode in GameModes:
    column = 0 if GameModes[game_mode.name].value < 3 else 4
    row = (
        GameModes[game_mode.name].value
        if GameModes[game_mode.name].value < 3
        else GameModes[game_mode.name].value - 3
    )
    mode_button = tk.Button(
        root,
        text=game_mode.name,
        font=("Arial", 14),
        command=lambda mode=game_mode: set_game_mode(mode),
    )
    mode_button.grid(row=row, column=column)
    mode_buttons[mode_button] = game_mode

set_game_mode(GameModes.MINIMAX)
reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
reset_button.grid(row=4, column=0, columnspan=5)

root.mainloop()
