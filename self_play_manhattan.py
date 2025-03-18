import itertools
import random


def score_guess(guess, code):
    """
    Returns the Manhattan (taxicab) distance between the guess and code.
    guess and code are tuples/lists of the same length.
    """
    return sum(abs(g - c) for g, c in zip(guess, code))


def all_codes(num_colors=6, num_positions=4):
    """
    Generate all possible codes as tuples, e.g. (1,1,2,2).
    """
    return list(itertools.product(range(1, num_colors + 1), repeat=num_positions))


def code_to_int(code, num_colors=6):
    """
    Convert a code tuple into an integer for tie-breaking.
    """
    val = 0
    for digit in code:
        val = val * num_colors + (digit - 1)
    return val


def minimax_pick(S, all_guesses):
    """
    Minimax strategy for Manhattan distance feedback.
    """
    best_guesses = []
    best_worst_case = None

    for guess in all_guesses:
        partition = {}
        for code in S:
            distance = score_guess(guess, code)
            partition[distance] = partition.get(distance, 0) + 1

        wc_size = max(partition.values(), default=0)

        if best_worst_case is None or wc_size < best_worst_case:
            best_worst_case = wc_size
            best_guesses = [guess]
        elif wc_size == best_worst_case:
            best_guesses.append(guess)

    # Prefer guesses in S and break ties numerically
    in_S = [g for g in best_guesses if g in S]
    final_candidates = in_S if in_S else best_guesses
    final_candidates.sort(key=lambda c: code_to_int(c))
    return final_candidates[0]


def self_play_mastermind(num_colors=6, num_positions=4):
    """
    Self-play Mastermind with Manhattan distance scoring.
    """
    Omega = all_codes(num_colors, num_positions)
    secret_code = random.choice(Omega)
    S = Omega[:]

    print("=== Mastermind Self-Play (Manhattan Distance) ===")
    print(f"Secret code (unknown to solver): {secret_code}")

    # Start with a central guess for better initial partitioning
    mid_color = (num_colors // 2) + 1
    guess = tuple([mid_color] * num_positions)

    guess_count = 0
    while True:
        guess_count += 1
        distance = score_guess(guess, secret_code)

        print(f"[Guess #{guess_count}] {guess} => Distance: {distance}")

        if distance == 0:
            print(f"\nSolved in {guess_count} guesses!")
            break

        # Filter possible codes using Manhattan distance
        S = [c for c in S if score_guess(guess, c) == distance]

        if not S:
            print("Error: No consistent codes remaining")
            break

        # Get next guess using minimax strategy
        guess = minimax_pick(S, Omega)


if __name__ == "__main__":
    self_play_mastermind()