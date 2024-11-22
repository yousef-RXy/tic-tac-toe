import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import threading
import math
import copy


def print_board(current_board):
    with lock:
        print("Current board:")
        for i in range(3):
            print(
                f"{current_board[i][0]} | {current_board[i][1]} | {current_board[i][2]}"
            )
            print("--+---+---")
        print()


def minimax(depth, is_maximizing):
    global PLAYER_O, PLAYER_X, board

    current_board = copy.deepcopy(board)
    printer.submit(lambda: print_board(current_board))

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
                    eval = minimax(depth + 1, False)
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = PLAYER_O
                    eval = minimax(depth + 1, True)
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
        return min_eval


def minimax_with_alpha_beta(depth, is_maximizing, alpha, beta):
    global PLAYER_O, PLAYER_X, board

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


def ai_move():
    global board, buttons, PLAYER_X

    best_val = -math.inf
    ai_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = PLAYER_X
                move_val = minimax(0, False)
                board[i][j] = " "
                if move_val > best_val:
                    best_val = move_val
                    ai_move = (i, j)

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


PLAYER_X = "X"
PLAYER_O = "O"
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
        buttons[i][j].grid(row=i + 1, column=j)

reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
reset_button.grid(row=0, column=0, columnspan=3)

# reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
# reset_button.grid(row=4, column=0)
# reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
# reset_button.grid(row=4, column=1)
# reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
# reset_button.grid(row=4, column=2)

root.mainloop()
