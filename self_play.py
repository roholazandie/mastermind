import itertools
import random
from collections import Counter


def score_guess(guess, code):
    """
    Returns (A, B) where:
      A = number of exact matches,
      B = number of correct colors but in wrong positions
    guess and code are tuples/lists of the same length.
    """
    # A: exact matches
    A = sum(g == c for g, c in zip(guess, code))

    # B: total color matches - exact matches
    guess_count = Counter(guess)
    code_count = Counter(code)
    color_matches = sum(min(guess_count[col], code_count[col]) for col in guess_count)
    B = color_matches - A

    return (A, B)


def all_codes(num_colors=6, num_positions=4):
    """
    Generate all possible codes as tuples, e.g. (1,1,2,2).
    """
    return list(itertools.product(range(1, num_colors + 1), repeat=num_positions))


def code_to_int(code, num_colors=6):
    """
    Convert a code tuple into an integer for tie-breaking:
    Interprets the code as a base-(num_colors) number.
    The smaller the integer, the 'smaller' the code.
    """
    val = 0
    for digit in code:
        val = val * num_colors + (digit - 1)
    return val


def minimax_pick(S, all_guesses):
    """
    Given:
      S: the current set of *possible* secret codes.
      all_guesses: typically = all possible codes.
    Return:
      The guess (from all_guesses) that:
       1) Minimizes the worst-case partition of S across all responses.
       2) Among ties, prefer any guess that is in S.
       3) Among further ties, pick the guess with the smallest code_to_int().
    """
    best_guesses = []
    best_worst_case = None  # track minimal worst-case size

    for guess in all_guesses:
        partition = {}
        for code in S:
            resp = score_guess(guess, code)
            partition[resp] = partition.get(resp, 0) + 1

        wc_size = max(partition.values())  # worst-case subset size

        if best_worst_case is None or wc_size < best_worst_case:
            best_worst_case = wc_size
            best_guesses = [guess]
        elif wc_size == best_worst_case:
            best_guesses.append(guess)

    # Among all best guesses, prefer one that is in S if possible
    in_S = [g for g in best_guesses if g in S]
    if in_S:
        final_candidates = in_S
    else:
        final_candidates = best_guesses

    # Tie-break by smallest code_to_int
    final_candidates.sort(key=lambda c: code_to_int(c))
    return final_candidates[0]


def self_play_mastermind(num_colors=6, num_positions=4):
    """
    Self-play Mastermind:
      - Randomly generate a secret code.
      - Use Knuth's minimax strategy to guess until we find it.
      - Print each guess and feedback.
    """
    # 1) All possible codes
    Omega = all_codes(num_colors, num_positions)

    # 2) Pick a random secret code (the "game")
    secret_code = random.choice(Omega)

    # 3) Initialize S = all possible solutions
    S = Omega[:]

    print("=== Mastermind Self-Play ===")
    print(f"Secret code (unknown to solver): {secret_code}")

    # Knuth suggested first guess (for 6-colors 4-positions) is (1,1,2,2).
    guess = (1, 1, 2, 2)

    guess_count = 0
    while True:
        guess_count += 1

        # Score the guess against the secret code
        (A, B) = score_guess(guess, secret_code)

        # Print the guess and the resulting feedback
        print(f"[Guess #{guess_count}] Guess: {guess} => Feedback: A={A}, B={B}")

        if A == num_positions:
            print(f"\nSolver found the secret code in {guess_count} guess(es)!")
            break

        # Filter S to keep only codes consistent with the feedback
        S = [c for c in S if score_guess(guess, c) == (A, B)]

        if not S:
            print("No codes left consistent with that feedback. (Shouldn't happen unless there's an error.)")
            break

        # Next guess: minimax from the updated S
        guess = minimax_pick(S, Omega)


if __name__ == "__main__":
    self_play_mastermind()
