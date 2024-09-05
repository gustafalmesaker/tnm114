import random

# Constants for the board size
BOARD_SIZE = 5

# Symbols for the board
EMPTY = "-"
SHIP = "S"
HIT = "X"
MISS = "O"

# Create an empty board
def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# Display the board (for debugging or visualizing)
def print_board(board):
    for row in board:
        print(" ".join(row))
    print("\n")

# Randomly place ships on the board
def place_ships(board, num_ships):
    ships_placed = 0
    while ships_placed < num_ships:
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        if board[row][col] == EMPTY:
            board[row][col] = SHIP
            ships_placed += 1

# Player fires at the board
def fire(board, row, col):
    if board[row][col] == SHIP:
        board[row][col] = HIT
        return "Hit!"
    elif board[row][col] == EMPTY:
        board[row][col] = MISS
        return "Miss!"
    else:
        return "Already fired there!"

# Check if all ships are sunk
def all_ships_sunk(board):
    for row in board:
        if SHIP in row:
            return False
    return True

# Main game loop
def play_game():
    player_board = create_board()
    ai_board = create_board()

    # Place ships for player and AI (for now random)
    place_ships(player_board, 3)
    place_ships(ai_board, 3)

    game_over = False
    while not game_over:
        # Display boards (for now both visible)
        print("Your board:")
        print_board(player_board)
        print("AI board:")
        print_board(ai_board)

        # Player's turn
        print("Your turn!")
        row = int(input("Enter row: "))
        col = int(input("Enter col: "))
        result = fire(ai_board, row, col)
        print(result)

        # Check if AI's ships are sunk
        if all_ships_sunk(ai_board):
            print("You win!")
            game_over = True
            break

        # AI's turn (for now random)
        print("AI's turn!")
        row, col = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        result = fire(player_board, row, col)
        print(f"AI fires at ({row}, {col}) - {result}")

        # Check if player's ships are sunk
        if all_ships_sunk(player_board):
            print("AI wins!")
            game_over = True

# Start the game
play_game()
