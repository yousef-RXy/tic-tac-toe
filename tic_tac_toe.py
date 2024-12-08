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


def minimax(depth, is_maximizing, reduction=None, all_boards=None):
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

    if reduction == Reduction.SYMMETRY_REDUCTION:
        symmetries = [tuple(map(tuple, sym)) for sym in generate_symmetries()]
        main_board = min(symmetries)
        if main_board in all_boards:
            return all_boards[main_board]

    if is_maximizing:
        max_eval = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_X
                    eval = minimax(depth + 1, False, reduction, all_boards)
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_O
                    eval = minimax(depth + 1, True, reduction, all_boards)
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = min_eval
        return min_eval


def minimax_with_heretic(
    depth, is_maximizing, heuristic, reduction, max_depth=math.inf, all_boards=None
):
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

    if reduction == Reduction.HEURISTIC_REDUCTION:
        if depth >= max_depth:
            return heuristic()
    elif reduction == Reduction.SYMMETRY_REDUCTION:
        symmetries = [tuple(map(tuple, sym)) for sym in generate_symmetries()]
        main_board = min(symmetries)
        if main_board in all_boards:
            return all_boards[main_board]

    if is_maximizing:
        max_eval = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_X
                    eval = minimax_with_heretic(
                        depth + 1, False, heuristic, reduction, max_depth, all_boards
                    )
                    if Reduction.HEURISTIC_REDUCTION:
                        max_eval = max(max_eval, eval)
                    else:
                        max_eval = max(max_eval, eval, heuristic())

                    board[i][j] = " "
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_O
                    eval = minimax_with_heretic(
                        depth + 1, True, heuristic, reduction, max_depth, all_boards
                    )

                    if Reduction.HEURISTIC_REDUCTION:
                        min_eval = min(min_eval, eval)
                    else:
                        min_eval = min(min_eval, eval, heuristic())

                    board[i][j] = " "
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = min_eval
        return min_eval


def minimax_with_alpha_beta(
    depth, is_maximizing, alpha, beta, reduction=None, all_boards=None
):
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

    if reduction == Reduction.SYMMETRY_REDUCTION:
        symmetries = [tuple(map(tuple, sym)) for sym in generate_symmetries()]
        main_board = min(symmetries)
        if main_board in all_boards:
            return all_boards[main_board]

    if is_maximizing:
        max_eval = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_X
                    eval = minimax_with_alpha_beta(
                        depth + 1, False, alpha, beta, reduction, all_boards
                    )
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = max_eval
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
                    eval = minimax_with_alpha_beta(
                        depth + 1, True, alpha, beta, reduction, all_boards
                    )
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
                    if reduction == Reduction.SYMMETRY_REDUCTION:
                        all_boards[main_board] = min_eval
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


def generate_symmetries():
    global board
    symmetries = []
    symmetries.append(board)
    curr_board = rotate_90(board)
    symmetries.append(curr_board)

    for i in range(2):
        curr_board = rotate_90(curr_board)
        symmetries.append(curr_board)
        symmetries.append(reflect_horizontal(curr_board))
        symmetries.append(reflect_vertical(curr_board))

    return symmetries


def rotate_90(board):
    return [[board[2 - j][i] for j in range(3)] for i in range(3)]


def reflect_horizontal(board):
    return [row[::-1] for row in board]


def reflect_vertical(board):
    return board[::-1]


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
                elif current_game_mode == GameModes.HEURISTIC_1_SYMMETRY_REDUCTION:
                    move_val = minimax_with_heretic(
                        0,
                        False,
                        check_winning_lines_heuristic,
                        Reduction.SYMMETRY_REDUCTION,
                        all_boards={},
                    )
                elif current_game_mode == GameModes.HEURISTIC_2_SYMMETRY_REDUCTION:
                    move_val = minimax_with_heretic(
                        0,
                        False,
                        combined_heuristic,
                        Reduction.SYMMETRY_REDUCTION,
                        all_boards={},
                    )
                elif current_game_mode == GameModes.HEURISTIC_1_HEURISTIC_REDUCTION:
                    move_val = minimax_with_heretic(
                        0,
                        False,
                        check_winning_lines_heuristic,
                        Reduction.HEURISTIC_REDUCTION,
                        max_depth=4,
                    )
                elif current_game_mode == GameModes.HEURISTIC_2_HEURISTIC_REDUCTION:
                    move_val = minimax_with_heretic(
                        0,
                        False,
                        combined_heuristic,
                        Reduction.HEURISTIC_REDUCTION,
                        max_depth=3,
                    )
                elif current_game_mode == GameModes.MINIMAX_SYMMETRY_REDUCTION:
                    move_val = minimax(
                        0, False, Reduction.SYMMETRY_REDUCTION, all_boards={}
                    )
                elif current_game_mode == GameModes.ALPHA_BETA_SYMMETRY_REDUCTION:
                    move_val = minimax_with_alpha_beta(
                        0,
                        False,
                        -math.inf,
                        math.inf,
                        Reduction.SYMMETRY_REDUCTION,
                        all_boards={},
                    )

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
    MINIMAX_SYMMETRY_REDUCTION = 2
    ALPHA_BETA_SYMMETRY_REDUCTION = 3
    HEURISTIC_1_SYMMETRY_REDUCTION = 4
    HEURISTIC_2_SYMMETRY_REDUCTION = 5
    HEURISTIC_1_HEURISTIC_REDUCTION = 6
    HEURISTIC_2_HEURISTIC_REDUCTION = 7


class Reduction(Enum):
    SYMMETRY_REDUCTION = 0
    HEURISTIC_REDUCTION = 1


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
    column = 0 if GameModes[game_mode.name].value < 4 else 4
    row = (
        GameModes[game_mode.name].value
        if GameModes[game_mode.name].value < 4
        else GameModes[game_mode.name].value - 4
    )
    button_text = " ".join(game_mode.name.split("_"))
    if len(button_text) > len(" ".join(GameModes.ALPHA_BETA.name.split("_"))):
        words = button_text.split(" ")
        midpoint = int(len(words) / 2)
        button_text = "\n".join(
            [" ".join(words[:midpoint]), " ".join(words[midpoint:])]
        )

    mode_button = tk.Button(
        root,
        text=button_text,
        font=("Arial", 14),
        command=lambda mode=game_mode: set_game_mode(mode),
    )
    mode_button.grid(row=row, column=column)
    mode_buttons[mode_button] = game_mode

set_game_mode(GameModes.MINIMAX)
reset_button = tk.Button(
    root, text="Reset", font=("Arial", 14), height=2, command=reset_game
)
reset_button.grid(row=3, column=1, columnspan=3)

root.mainloop()
