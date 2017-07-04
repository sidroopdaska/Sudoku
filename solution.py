__author__ = "Siddharth Sharma"
"""solution.py: Sudoku puzzle solving algorithm
"""

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(A, B):
    """
    Performs a cross multiplication of two strings.
    :param A: string
    :param B: string
    :return: List formed by all the possible concatenations of a letter s in string A with a letter t in string B.
    """
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

forward_diagonal = [rows[i] + cols[i] for i in range(len(rows))]
reverse_diagonal = [rows[i] + cols[len(cols) - 1 - i] for i in range(len(rows))]
diagonal_list = [forward_diagonal, reverse_diagonal]

unit_list = row_units + column_units + square_units + diagonal_list
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    naked_twin_instances = dict()

    # Iterate over all units
    for unit in unit_list:
        unit_value_dict = dict()
        for box in unit:
            box_value = values[box]
            if box_value in unit_value_dict.keys():
                unit_value_dict[box_value].append(box)
            else:
                unit_value_dict[box_value] = [box]

        # Filter naked twins from the dictionary of one unit values
        for k, v in unit_value_dict.items():
            if len(k) == 2 and len(v) == 2:
                if k in naked_twin_instances.keys():
                    if v not in naked_twin_instances[k]:
                        naked_twin_instances[k].append(v)
                else:
                    naked_twin_instances[k] = [v]

    # Eliminate the naked twins as possibilities for their peers
    for k, v in naked_twin_instances.items():
        for naked_twin in v:
            # Perform a union of the peers of each of the twin in a naked twin set
            naked_twin_peers = peers[naked_twin[0]].intersection(peers[naked_twin[1]])
            unique_peers = naked_twin_peers - set(naked_twin)
            for digit in k:
                for peer in unique_peers:
                    if digit in values[peer]:
                        values = assign_value(values, peer, values[peer].replace(digit, ""))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = dict(zip(boxes, grid))
    for k, v in values.items():
        if v == '.':
            values = assign_value(values, k, '123456789')

    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """
    Implementation of the Elimination strategy
    :param values: Dictionary of the form {'box_name': '123456789', ...}
    :return: Dictionary with the updated box values of the form {'box_name': '123456789', ...}
    """
    for k, v in values.items():
        if len(v) == 1:
            for peer in peers[k]:
                if v in values[peer]:
                    values = assign_value(values, peer, values[peer].replace(v, ""))

    return values


def only_choice(values):
    """
    Implementation of the Only Choice strategy
    :param values: Dictionary of the form {'box_name': '123456789', ...}
    :return: Dictionary with the updated box values of the form {'box_name': '123456789', ...}
    """
    for unit in unit_list:
        digits = '123456789'
        for digit in digits:
            digit_occurrences = [box for box in unit if digit in values[box]]
            if len(digit_occurrences) == 1:
                values = assign_value(values, digit_occurrences[0], digit)


def reduce_puzzle(values):
    """
    Reduces the possible set of solutions for each box in the grid using Constraint Propagation
    :param values: Dictionary of the form {'box_name': '123456789', ...}
    :return: Dictionary with the updated box values. False if a box contains no value.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        eliminate(values)
        # Use the Only Choice Strategy
        only_choice(values)
        # Use the Naked Twin Strategy
        naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """
    Implementation of the Depth First Search strategy to find grid solution when the
    Constraint Propagation gets stalled
    :param values: Dictionary of the form {'box_name': '123456789', ...}
    :return: Dictionary with the updated box values. False if no solution is found.
    """
    values = reduce_puzzle(values)
    if values is False:
        return False

    if all(len(values[box]) == 1 for box in boxes):
        return values

    unsolved_boxes = [box for box in boxes if len(values[box]) > 1]
    unsolved_boxes.sort(key=lambda x: len(values[x]))

    box = unsolved_boxes[0]
    value = values[box]
    for j in range(len(value)):
        new_values = values.copy()
        new_values = assign_value(new_values, box, value[j])
        attempt = search(new_values)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    solved_grid_values = search(values)
    return solved_grid_values


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))