"""AI controller for automated Snake gameplay."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from ..game.engine import GameState
from ..game.snake import Direction
from .pathfinding import bfs_path, evaluate_move_safety, find_safe_moves

if TYPE_CHECKING:
    from ..config import Config

AIStrategy = Literal["greedy", "bfs_safe", "survival", "commit_hunter"]


@dataclass
class AIController:
    """AI controller that decides snake movement."""

    config: "Config"

    def get_next_direction(self, state: GameState) -> Direction:
        """Determine the next direction for the snake.

        Args:
            state: Current game state.

        Returns:
            The direction to move.
        """
        strategy = self.config.ai_strategy

        if strategy == "greedy":
            return self._greedy_move(state)
        elif strategy == "bfs_safe":
            return self._bfs_safe_move(state)
        elif strategy == "survival":
            return self._survival_move(state)
        elif strategy == "commit_hunter":
            return self._commit_hunter_move(state)
        else:
            return self._bfs_safe_move(state)

    def _commit_hunter_move(self, state: GameState) -> Direction:
        """Prioritize visible commit chasing in food mode.

        Strategy:
        1. Collect remaining contribution cells.
        2. Rank by distance to current head.
        3. Search the top nearest targets for safe, short BFS paths.
        4. Tie-break by continuing direction, then target contribution level.
        5. Fallback to survival when no safe target path exists.
        """
        snake = state.snake
        board = state.board
        safe_moves = find_safe_moves(snake, board)

        if not safe_moves:
            return snake.direction

        if self.config.contribution_mode != "food":
            return self._bfs_safe_move(state)

        obstacles = set(list(snake.body)[:-1])
        if snake.growing:
            obstacles.add(snake.tail)

        candidate_targets = board.get_contribution_positions(
            exclude=snake.get_body_positions(),
            min_level=1,
        )

        if not candidate_targets:
            return self._best_survival_move(state, safe_moves)

        head = snake.head
        candidate_targets.sort(
            key=lambda pos: (
                abs(pos.x - head.x) + abs(pos.y - head.y),
                abs(pos.y - head.y),
                abs(pos.x - head.x),
            )
        )

        best_direction: Direction | None = None
        best_rank: tuple[int, int, int] | None = None
        min_safe_space = snake.length + 2

        for target in candidate_targets[:12]:
            path = bfs_path(head, target, board, obstacles)
            if not path:
                continue

            next_direction = path[0]
            if next_direction not in safe_moves:
                continue

            safety = evaluate_move_safety(snake, next_direction, board)
            if safety < min_safe_space:
                continue

            target_level = board.cells[target.y][target.x].contribution_level
            rank = (
                len(path),
                0 if next_direction == snake.direction else 1,
                -target_level,
            )

            if best_rank is None or rank < best_rank:
                best_rank = rank
                best_direction = next_direction

        if best_direction is not None:
            return best_direction

        return self._best_survival_move(state, safe_moves)

    def _greedy_move(self, state: GameState) -> Direction:
        """Simple greedy strategy: move towards food if safe.

        Args:
            state: Current game state.

        Returns:
            Direction to move.
        """
        snake = state.snake
        food = state.food
        board = state.board

        safe_moves = find_safe_moves(snake, board)

        if not safe_moves:
            # No safe moves, keep current direction
            return snake.direction

        if food is None:
            # No food, pick a safe direction
            return safe_moves[0]

        # Try to move towards food
        head = snake.head
        dx = food.x - head.x
        dy = food.y - head.y

        # Prefer horizontal or vertical based on distance
        preferred: list[Direction] = []
        if abs(dx) > abs(dy):
            if dx > 0 and Direction.RIGHT in safe_moves:
                preferred.append(Direction.RIGHT)
            elif dx < 0 and Direction.LEFT in safe_moves:
                preferred.append(Direction.LEFT)
            if dy > 0 and Direction.DOWN in safe_moves:
                preferred.append(Direction.DOWN)
            elif dy < 0 and Direction.UP in safe_moves:
                preferred.append(Direction.UP)
        else:
            if dy > 0 and Direction.DOWN in safe_moves:
                preferred.append(Direction.DOWN)
            elif dy < 0 and Direction.UP in safe_moves:
                preferred.append(Direction.UP)
            if dx > 0 and Direction.RIGHT in safe_moves:
                preferred.append(Direction.RIGHT)
            elif dx < 0 and Direction.LEFT in safe_moves:
                preferred.append(Direction.LEFT)

        if preferred:
            return preferred[0]

        return safe_moves[0]

    def _bfs_safe_move(self, state: GameState) -> Direction:
        """BFS pathfinding with safety checks.

        This strategy:
        1. Finds a path to food using BFS
        2. Only follows the path if it leads to a position with enough escape room
        3. Falls back to survival mode if no good path exists

        Args:
            state: Current game state.

        Returns:
            Direction to move.
        """
        snake = state.snake
        food = state.food
        board = state.board

        safe_moves = find_safe_moves(snake, board)

        if not safe_moves:
            return snake.direction

        if food is None:
            return self._best_survival_move(state, safe_moves)

        # Get obstacles (snake body excluding tail)
        obstacles = set(list(snake.body)[:-1])
        if snake.growing:
            obstacles.add(snake.tail)

        # Find path to food
        path = bfs_path(snake.head, food, board, obstacles)

        if path:
            next_direction = path[0]

            # Check if this move is safe (leads to enough space)
            space_after_move = evaluate_move_safety(snake, next_direction, board)

            # Need at least snake length + some buffer of reachable cells
            min_safe_space = snake.length + 5

            if space_after_move >= min_safe_space:
                return next_direction

        # No safe path to food, use survival strategy
        return self._best_survival_move(state, safe_moves)

    def _survival_move(self, state: GameState) -> Direction:
        """Pure survival strategy: maximize escape routes.

        Args:
            state: Current game state.

        Returns:
            Direction to move.
        """
        safe_moves = find_safe_moves(state.snake, state.board)

        if not safe_moves:
            return state.snake.direction

        return self._best_survival_move(state, safe_moves)

    def _best_survival_move(
        self,
        state: GameState,
        safe_moves: list[Direction],
    ) -> Direction:
        """Find the move that maximizes reachable space.

        Args:
            state: Current game state.
            safe_moves: List of safe directions.

        Returns:
            The best direction for survival.
        """
        if not safe_moves:
            return state.snake.direction

        # Evaluate each safe move
        move_scores: list[tuple[Direction, int]] = []

        for direction in safe_moves:
            score = evaluate_move_safety(state.snake, direction, state.board)
            move_scores.append((direction, score))

        # Sort by score (highest first)
        move_scores.sort(key=lambda x: x[1], reverse=True)

        return move_scores[0][0]
