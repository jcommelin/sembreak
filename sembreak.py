import argparse
import pysbd
import re
import sys

# Reformat a file according to semantic linebreaking.

# Recursively find the optimal break points within a range of indices (excluding `end`)
# The cost function `cost_fun(i, j)` should return the cost of the segment `[i, ..., j-1]`
# The maximum cost `max_cost` should be a large value,
# larger than the cost of the sum of `cost_fun(i, i+1)` for all `i`
#
# Returns a list of indices of the optimal break points,
# where an index `i` indicates a break point `..., i-1], [i, ...`
def find_breaks(start, end, cost_fun, max_cost):
    # Initialize memoization dictionary
    memo = {}
    def aux(m, n, level=1):
        # Base case: no break points
        if m == n:
            return (0, [])
        # Check if the solution is already memoized
        if (m, n) in memo:
            return memo[(m, n)]
        # Initialize the minimum cost array
        min_cost = max_cost
        best_breaks = list(range(m, n))
        # Iterate through all possible break points
        for i in range(m, n):
            (cost, breaks) = aux(m, i, level+1)
            cost += cost_fun(i, n)
            if cost < min_cost:
                min_cost = cost
                best_breaks = breaks + [i]
        memo[(m, n)] = (min_cost, best_breaks)
        return (min_cost, best_breaks)
    return aux(start, end)[1]

def semantic_break(sentence, max_line_length=80):
    if len(sentence) <= max_line_length:
        yield sentence
        return
    
    # Todo: ideally we would like to prioritize certain delimiters over others

    # Define delimiters that may be preceded (resp. followed) by a newline character
    break_before_delimiters = ' \('
    break_after_delimiters = ',|;|:|\band\b|\bor\b|\) '

    # Replace each delimiter with the same delimiter preceded (resp. followed) by a newline character
    sentence = re.sub(break_before_delimiters, r'\n\g<0>', sentence)
    sentence = re.sub(break_after_delimiters, r'\g<0>\n', sentence)

    # Split the sentence into pieces at each newline character
    pieces = [piece.strip() for piece in sentence.split('\n')]

    # Precompute the lengths of the pieces and the number of pieces
    lengths = [len(piece) for piece in pieces]
    N = len(lengths)

    # Define the cost function
    def cost(i, j):
        length = sum(lengths[i:j]) + (j - i - 1)
        if length > max_line_length:
            return length**2
        else:
            return (max_line_length - length)**2

    # Compute the maximum possible cost
    max_cost = sum(cost(i, i+1) for i in range(N))

    # Find the optimal break points
    breaks = find_breaks(0, N, cost, max_cost)

    # Yield the lines
    k = len(breaks)
    breaks.append(N)
    for i in range(k):
        yield ' '.join(pieces[breaks[i]:breaks[i+1]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("max_line_length", type=int, nargs='?', default=80)
    args = parser.parse_args()

    text = sys.stdin.read()

    # Bug(pysbd):
    # a parenthetical sentence ends up being split between the period and the closing parenthesis
    seg = pysbd.Segmenter(language="en", clean=False)
    sentences = seg.segment(text)
    
    for sentence in sentences:
        for line in semantic_break(sentence, args.max_line_length):
            print(line)
