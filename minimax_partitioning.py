def can_partition(nums, k, limit):
    """
    Check if 'nums' can be split into at most 'k' subsets
    such that no subset sum exceeds 'limit'.
    """
    subset_count = 1
    current_sum = 0

    for num in nums:
        # If a single number is bigger than limit, it's impossible
        if num > limit:
            return False

        if current_sum + num <= limit:
            current_sum += num
        else:
            # Need a new subset
            subset_count += 1
            current_sum = num

            if subset_count > k:
                return False

    return True


def minimax_partition_with_subsets(nums, k):
    """
    Returns:
      - The minimized maximum subset sum (int)
      - A partition (list of lists) of 'nums' into <= k subsets
        achieving that minimized maximum.
    """
    # Binary search bounds
    left, right = max(nums), sum(nums)
    answer = right

    # 1) Find the minimal feasible limit
    while left <= right:
        mid = (left + right) // 2
        if can_partition(nums, k, mid):
            answer = mid
            right = mid - 1
        else:
            left = mid + 1

    # 2) Reconstruct a valid partition under 'answer'
    #    (greedily from left to right)
    subsets = []
    current_subset = []
    current_sum = 0

    for num in nums:
        if current_sum + num <= answer:
            current_subset.append(num)
            current_sum += num
        else:
            # Start a new subset
            subsets.append(current_subset)
            current_subset = [num]
            current_sum = num

    # Append the last subset
    if current_subset:
        subsets.append(current_subset)

    return answer, subsets


# ------------------------------
# Example usage:
if __name__ == "__main__":
    arr = [3, 5, 6, 8, 9]
    k = 2
    minimax_val, partition = minimax_partition_with_subsets(arr, k)

    print("Minimized maximum subset sum:", minimax_val)
    print("Partition (<= k subsets):", partition)
