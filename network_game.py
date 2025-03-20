import numpy as np
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def generate_random_graph(n, p, seed=None):
    """
    Generate an undirected Erdős–Rényi graph with n nodes and edge probability p.
    Use a plain Python int as the seed to avoid NumPy integer issues.
    """
    # If 'seed' is a NumPy int, cast it to a Python int
    if isinstance(seed, np.integer):
        seed = int(seed)
    G = nx.erdos_renyi_graph(n, p, seed=seed, directed=False)
    return G


def generate_pairwise_payoffs(G, low=-1.0, high=1.0, seed=None):
    """
    For each edge (i, j) in G, generate a random 2x2 payoff matrix for i.
    The payoff matrix for j is then the negative of that (pairwise zero-sum).
    We'll store them in a dictionary payoff[i][j], which is a 2x2 numpy array.
    """
    rng = np.random.default_rng(seed)

    # payoff[i][j] = 2x2 payoff matrix for i, if edge i-j exists
    payoff = {}
    for i in G.nodes():
        payoff[i] = {}

    for (i, j) in G.edges():
        M_ij = rng.uniform(low, high, size=(2, 2))  # 2x2 random for i
        payoff[i][j] = M_ij
        payoff[j][i] = -M_ij  # zero-sum for j
    return payoff


def best_response(i, current_actions, payoff, neighbors):
    """
    Compute the *myopic best response* for player i: choose the action (0 or 1)
    that maximizes the sum of payoffs from edges (i, j), given neighbors' actions.
    """
    neigh = neighbors[i]
    best_act = None
    best_val = -float('inf')

    for candidate_a_i in [0, 1]:
        total_payoff = 0.0
        for j in neigh:
            a_j = current_actions[j]
            total_payoff += payoff[i][j][candidate_a_i, a_j]
        if total_payoff > best_val:
            best_val = total_payoff
            best_act = candidate_a_i

    return best_act


def update_all_players(actions, payoff, neighbors):
    """
    Perform a synchronous best-response update:
    each player picks best_response(...) to the current actions of neighbors.
    """
    new_actions = {}
    for i in actions.keys():
        new_actions[i] = best_response(i, actions, payoff, neighbors)
    return new_actions


def compute_profile_payoffs(actions, payoff, neighbors):
    """
    Compute each player's payoff under the given action profile.
    """
    payoffs = {}
    for i in actions:
        a_i = actions[i]
        p_i = 0.0
        for j in neighbors[i]:
            a_j = actions[j]
            p_i += payoff[i][j][a_i, a_j]
        payoffs[i] = p_i
    return payoffs


def run_best_response_dynamics(G, payoff, max_iter=20):
    """
    Run iterative best-response dynamics for up to max_iter steps
    or until no player changes action.

    Returns 'history': a list of (actions, payoffs) snapshots at each iteration.
    """
    neighbors = {i: list(G.neighbors(i)) for i in G.nodes()}
    rng = np.random.default_rng()

    # Initialize actions randomly (0 or 1)
    actions = {i: rng.integers(0, 2) for i in G.nodes()}

    history = []

    for step in range(max_iter):
        payoffs = compute_profile_payoffs(actions, payoff, neighbors)
        history.append((actions.copy(), payoffs.copy()))

        new_actions = update_all_players(actions, payoff, neighbors)

        # Check if stable (no changes)
        if all(new_actions[i] == actions[i] for i in G.nodes()):
            # Record final
            actions = new_actions
            payoffs = compute_profile_payoffs(actions, payoff, neighbors)
            history.append((actions.copy(), payoffs.copy()))
            break

        actions = new_actions

    return history


def animate_history(G, history):
    """
    Create a Matplotlib animation showing how the best-response dynamics
    evolve over iterations.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    pos = nx.spring_layout(G, seed=42)  # consistent layout

    # Draw edges once (they don't change)
    nx.draw_networkx_edges(G, pos, ax=ax)

    # We'll create a single scatter-plot of nodes and update colors each frame.
    # We must pass 'nodelist=...' and 'node_color=...' explicitly:
    node_collection = nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=G.nodes(),  # which nodes to draw
        node_color=["white"] * G.number_of_nodes(),  # initial placeholder
        node_size=600,
        ax=ax
    )

    # Create text labels for each node. We'll update them each frame.
    node_texts = {}
    for node in G.nodes():
        text = ax.text(
            pos[node][0],
            pos[node][1],
            str(node),
            ha="center",
            va="center",
            color="black",
            fontsize=10,
            fontweight="bold"
        )
        node_texts[node] = text

    ax.set_title("Best-Response Dynamics")
    ax.set_axis_off()

    def init():
        # Initialization function for FuncAnimation (no special action needed)
        return (node_collection, *node_texts.values())

    def update(frame):
        # Each frame corresponds to one iteration snapshot
        actions, payoffs = history[frame]

        # Color each node by its action
        colors = []
        for node in G.nodes():
            a = actions[node]
            if a == 0:
                colors.append("lightgray")
            else:
                colors.append("skyblue")
        node_collection.set_facecolor(colors)

        # Update text to show payoff
        for node in G.nodes():
            node_texts[node].set_text(f"{node}\n({payoffs[node]:.2f})")

        ax.set_title(f"Best-Response Dynamics (Iteration {frame})")
        return (node_collection, *node_texts.values())

    # Create the animation
    ani = FuncAnimation(
        fig,
        update,
        frames=len(history),
        init_func=init,
        blit=False,  # True can be faster but sometimes glitchy with text changes
        interval=1000,  # ms between frames
        repeat=False
    )
    # save the animation as an mp4. This requires ffmpeg or mencoder to be installed.
    ani.save("best_response_dynamics.mp4", writer="ffmpeg")
    # plt.show()
    return ani


def main(n=6, p=0.5, max_iter=20, seed=42):
    """
    1) Create a random graph
    2) Generate random pairwise zero-sum payoffs
    3) Run best-response dynamics
    4) Animate the evolution
    """
    # 1) Random graph
    G = generate_random_graph(n, p, seed=seed)

    # 2) Random payoffs
    payoff = generate_pairwise_payoffs(G, seed=seed)

    # 3) Best-response dynamics
    history = run_best_response_dynamics(G, payoff, max_iter=max_iter)

    # Show final results in console
    print(f"Number of iterations recorded: {len(history)}")
    final_actions, final_payoffs = history[-1]
    print("Final actions:", final_actions)
    print("Final payoffs:", final_payoffs)

    # 4) Animate
    animate_history(G, history)


# Run the script
if __name__ == "__main__":
    main()
