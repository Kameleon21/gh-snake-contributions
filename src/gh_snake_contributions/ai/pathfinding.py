"""Pathfinding utilities for AI controller."""

from collections import deque

from ..game.board import Board, Position
from ..game.snake import Direction, Snake


def get_neighbors(pos: Position) -> list[tuple[Position, Direction]]:
    """Get all neighboring positions with their directions.

    Args:
        pos: The position to get neighbors for.

    Returns:
        List of (position, direction) tuples.
    """
    return [
        (pos + Direction.UP.value, Direction.UP),
        (pos + Direction.DOWN.value, Direction.DOWN),
        (pos + Direction.LEFT.value, Direction.LEFT),
        (pos + Direction.RIGHT.value, Direction.RIGHT),
    ]


def bfs_path(
    start: Position,
    target: Position,
    board: Board,
    obstacles: set[Position],
) -> list[Direction] | None:
    """Find the shortest path from start to target using BFS.

    Args:
        start: Starting position.
        target: Target position.
        board: The game board.
        obstacles: Set of positions that cannot be traversed.

    Returns:
        List of directions to reach target, or None if no path exists.
    """
    if start == target:
        return []

    visited: set[Position] = {start}
    queue: deque[tuple[Position, list[Direction]]] = deque([(start, [])])

    while queue:
        current, path = queue.popleft()

        for neighbor, direction in get_neighbors(current):
            if neighbor in visited:
                continue

            if neighbor == target:
                return path + [direction]

            if not board.is_walkable(neighbor):
                continue

            if neighbor in obstacles:
                continue

            visited.add(neighbor)
            queue.append((neighbor, path + [direction]))

    return None


def find_safe_moves(
    snake: Snake,
    board: Board,
) -> list[Direction]:
    """Find all directions that won't immediately kill the snake.

    Args:
        snake: The snake to check moves for.
        board: The game board.

    Returns:
        List of safe directions.
    """
    safe_moves: list[Direction] = []
    head = snake.head

    # Get body positions excluding tail (it will move)
    body_positions = set(list(snake.body)[:-1])
    if snake.growing:
        body_positions.add(snake.tail)

    for direction in Direction:
        # Skip reverse direction (would hit self immediately)
        if direction == snake.direction.opposite and snake.length > 1:
            continue

        next_pos = head + direction.value

        # Check if move is valid
        if not board.is_walkable(next_pos):
            continue

        # Check if move would hit body
        if next_pos in body_positions:
            continue

        safe_moves.append(direction)

    return safe_moves


def count_reachable_cells(
    start: Position,
    board: Board,
    obstacles: set[Position],
    max_count: int = 1000,
) -> int:
    """Count how many cells are reachable from a position.

    This is used to evaluate "escape routes" - moves that lead to
    larger open areas are generally safer.

    Args:
        start: Starting position.
        board: The game board.
        obstacles: Set of blocked positions.
        max_count: Maximum cells to count (optimization).

    Returns:
        Number of reachable cells.
    """
    visited: set[Position] = {start}
    queue: deque[Position] = deque([start])
    count = 0

    while queue and count < max_count:
        current = queue.popleft()
        count += 1

        for neighbor, _ in get_neighbors(current):
            if neighbor in visited:
                continue

            if not board.is_walkable(neighbor):
                continue

            if neighbor in obstacles:
                continue

            visited.add(neighbor)
            queue.append(neighbor)

    return count


def evaluate_move_safety(
    snake: Snake,
    direction: Direction,
    board: Board,
) -> int:
    """Evaluate how safe a move is based on reachable space.

    Args:
        snake: The snake.
        direction: Direction to evaluate.
        board: The game board.

    Returns:
        Number of cells reachable after making this move.
    """
    next_pos = snake.head + direction.value

    # Simulate where body will be after move
    new_body = set(list(snake.body)[:-1])
    new_body.add(snake.head)
    if snake.growing:
        new_body.add(snake.tail)

    return count_reachable_cells(next_pos, board, new_body)
