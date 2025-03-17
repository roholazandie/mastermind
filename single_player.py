import random


def score_guess(guess, code):
    """
    Given:
      guess: list of integers representing the guess.
      code:  list of integers representing the secret code.
    Returns:
      (A, B): A is the number of correct positions;
              B is the number of correct colors in wrong positions.
    """
    # A: number of exact matches
    A = sum(g == c for g, c in zip(guess, code))

    # To calculate B: total color matches minus the exact matches
    # 1. Count how many times each color appears in guess and in code
    # 2. Sum up the minimum count for each color (that is total color matches)
    # 3. Subtract A to get the number of correct colors in wrong positions
    color_count_guess = {}
    color_count_code = {}

    for g in guess:
        color_count_guess[g] = color_count_guess.get(g, 0) + 1
    for c in code:
        color_count_code[c] = color_count_code.get(c, 0) + 1

    total_color_matches = 0
    # sum of min counts of each color
    for color in color_count_guess:
        if color in color_count_code:
            total_color_matches += min(color_count_guess[color], color_count_code[color])

    B = total_color_matches - A
    return A, B


def play_mastermind(num_colors=6, num_positions=4):
    """
    Play a Mastermind-like game:
      - secret code has `num_positions` pegs
      - each peg is chosen from `1..num_colors`.
    """
    # Randomly generate the secret code
    secret_code = [random.randint(1, num_colors) for _ in range(num_positions)]

    print(f"Welcome to Mastermind!")
    print(f"The secret code has {num_positions} positions,")
    print(f"each a color from 1 to {num_colors}.")
    print("Enter your guesses as space-separated numbers, e.g. '1 2 3 4'.")
    print("Type 'exit' to quit.\n")

    while True:
        # Prompt user
        user_input = input(f"Enter your guess ({num_positions} numbers): ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Game exited.")
            break

        # Parse the guess
        guess_tokens = user_input.split()
        if len(guess_tokens) != num_positions:
            print(f"Please enter exactly {num_positions} numbers.\n")
            continue

        try:
            guess = list(map(int, guess_tokens))
        except ValueError:
            print("Invalid input (numbers only). Try again.\n")
            continue

        # Check range
        if any(not (1 <= g <= num_colors) for g in guess):
            print(f"Each color must be between 1 and {num_colors}.\n")
            continue

        # Compute score
        A, B = score_guess(guess, secret_code)
        print(f"Score: {A} correct position(s), {B} correct color(s) in wrong position(s).")

        if A == num_positions:
            print("Congratulations! You found the secret code!")
            break
        else:
            print("Try again.\n")


if __name__ == "__main__":
    # You can change the parameters as you wish:
    play_mastermind(num_colors=6, num_positions=4)
