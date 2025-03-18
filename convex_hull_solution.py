import random
import itertools


# -----------------------------
# 1) Basic Helper Functions
# -----------------------------

def all_codes(n, d):
    """
    Generate all codes as d-tuples from {1,...,n}.
    """
    return list(itertools.product(range(1, n + 1), repeat=d))


def hamming_distance(x, y):
    """
    Hamming distance: number of positions at which x and y differ.
    Here x,y are tuples of same length.
    """
    return sum(a != b for a, b in zip(x, y))


# -----------------------------
# 2) Convex Hull in 2D or 3D
#    (Quick demonstration approach)
# -----------------------------
#
# For higher dimensions, you'd typically use a specialized library
# (e.g. Qhull via scipy.spatial.ConvexHull). Here, we implement
# a minimal "Convex Hull" approach for d=2 or d=3 just to illustrate
# the concept. We'll do a fallback if d>3 or if you want more robust code.

import math


def convex_hull_2d(points):
    """
    Compute the 2D convex hull of a set of points using Graham scan or Andrew's monotone chain.
    Returns a list of vertices in CCW order.
    points: list of (x,y) in R^2
    """
    # Andrew's monotone chain algorithm
    # Sort points lexicographically
    pts = sorted(points)

    # Build lower hull
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenate lower + upper minus duplicate endpoints
    # upper[-1] is the same as lower[0], so we skip them
    return lower[:-1] + upper[:-1]


def cross(o, a, b):
    """
    Cross product of OA x OB in 2D
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def point_in_triangle(pt, tri):
    """
    Check if 2D point pt is inside or on boundary of triangle tri = (p1,p2,p3).
    Barycentric or cross-product method.
    """
    (p1, p2, p3) = tri
    c1 = cross(p1, p2, pt)
    c2 = cross(p2, p3, pt)
    c3 = cross(p3, p1, pt)

    # Check if all cross products have the same sign or zero
    # which indicates pt is on the same side (or boundary).
    # A quick way is to check the sign of the product of these cross values
    # but we must be careful with sign=0 cases. We'll do a consistent sign check:
    def same_sign(a, b):
        return a * b >= 0  # allows zero

    return (same_sign(c1, c2) and same_sign(c2, c3))


def all_integer_points_in_2d_hull(hull):
    """
    Given a 2D hull (list of vertices in CCW order),
    find all integer points inside or on the hull.

    We'll do a naive bounding box + point_in_polygon approach
    for demonstration.
    """
    # 1) bounding box
    xs = [p[0] for p in hull]
    ys = [p[1] for p in hull]
    minx, maxx = int(math.floor(min(xs))), int(math.ceil(max(xs)))
    miny, maxy = int(math.floor(min(ys))), int(math.ceil(max(ys)))

    # 2) Triangulate the hull or use a winding test. Let's do a simple
    #   "triangulate the polygon" approach:
    triangles = []
    for i in range(1, len(hull) - 1):
        tri = (hull[0], hull[i], hull[i + 1])
        triangles.append(tri)

    inside_points = []
    for ix in range(minx, maxx + 1):
        for iy in range(miny, maxy + 1):
            p = (ix, iy)
            # check if p is inside any triangle
            if point_in_polygon_2d(p, hull, triangles):
                inside_points.append(p)
    return inside_points


def point_in_polygon_2d(pt, hull, triangles):
    """
    Check if 'pt' is inside or on boundary of a polygon described by 'hull'.
    'triangles' is a fan triangulation from hull[0].
    We'll simply check if pt is in the union of those triangles.
    """
    for tri in triangles:
        if point_in_triangle(pt, tri):
            return True
    return False


# We'll omit an explicit 3D hull routine for brevity.
# For d>2, you'd typically do something like
#   from scipy.spatial import ConvexHull
# and gather integer points within it.

# -----------------------------
# 3) Main demonstration:
#    A small "Hamming Mastermind" with convex-hull coarsening
# -----------------------------
def play_hamming_mastermind_convex_hull(n=3, d=2):
    """
    Demonstration game:
      - Secret code c in {1..n}^d chosen at random.
      - We keep a set S of possible codes.
      - We guess (for example) the "centroid" of S (coordinate-wise average, rounded).
      - The puzzle returns the Hamming distance h.
      - We filter S to keep only codes consistent with h.
      - We compute the convex hull of those points in R^d,
        then reduce S to the integer points within that hull.
      - Repeat until found or S is empty.

    We do small n,d for demonstration so we can visualize or at least handle it easily.
    """
    # 1) All possible codes as a list of d-tuples
    S = all_codes(n, d)  # e.g. if n=3, d=2, S has 3^2=9 points.

    # 2) Pick secret code
    secret = random.choice(S)
    print("Secret code is:", secret)

    iteration = 0
    while True:
        iteration += 1

        # If S has only one element, guess that
        if len(S) == 1:
            guess = S[0]
        else:
            # A simple "centroid" guess:
            #   compute average in each coordinate, round
            #   then clamp to 1..n
            avg = [0] * d
            for x in S:
                for i in range(d):
                    avg[i] += x[i]
            sizeS = len(S)
            for i in range(d):
                avg[i] = avg[i] / sizeS
            # round and clamp
            guess = tuple(min(n, max(1, round(a))) for a in avg)

        # 3) Compute feedback: Hamming distance
        h = hamming_distance(guess, secret)

        print(f"\nIteration #{iteration}")
        print(f"  Current guess: {guess}")
        print(f"  Hamming distance = {h}")

        if h == 0:
            print("  Found the secret code!")
            break

        # 4) Filter S to keep only codes consistent with h
        new_S = [x for x in S if hamming_distance(guess, x) == h]

        # 5) "Convex hull" step in R^d. We'll do a naive approach:
        #    - If d=2, compute the polygon hull and keep integer points inside it.
        #    - If d>2, let's skip or just keep new_S as is.

        if d == 2:
            # embed new_S in R^2
            float_pts = [(float(x[0]), float(x[1])) for x in new_S]
            if len(float_pts) >= 3:
                hull_2d = convex_hull_2d(float_pts)
                # gather integer points in that hull
                hull_int_pts = all_integer_points_in_2d_hull(hull_2d)
                # intersect with the discrete set {1..n}^2
                # because we only want valid codes
                final_S = []
                valid_set = set(new_S)  # we only want those that were in new_S
                for ip in hull_int_pts:
                    ix, iy = ip
                    if (ix, iy) in valid_set:
                        final_S.append((ix, iy))
                S = final_S
            else:
                # if fewer than 3 points, hull is trivial
                S = new_S
        else:
            # For d != 2, we'll skip the hull step for brevity
            S = new_S

        print(f"  Possible space size after filtering + hull: {len(S)}")

        if len(S) == 0:
            print("  No possibilities left! (Something went wrong or feedback was inconsistent.)")
            break
        if len(S) <= 5:
            print("  Remaining possibilities:", S)


# -----------------------------
# Run a demo
# -----------------------------
if __name__ == "__main__":
    play_hamming_mastermind_convex_hull(n=3, d=2)
