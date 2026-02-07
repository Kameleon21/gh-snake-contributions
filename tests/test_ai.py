"""Tests for AI controller components."""

import pytest

from gh_snake_contributions.ai.controller import AIController
from gh_snake_contributions.ai.pathfinding import (
    bfs_path,
    evaluate_move_safety,
    find_safe_moves,
)
from gh_snake_contributions.config import Config
from gh_snake_contributions.game.board import Board, CellType, Position
from gh_snake_contributions.game.engine import GameEngine, GameState
from gh_snake_contributions.game.snake import Direction, Snake


class TestPathfinding:
    """Tests for pathfinding utilities."""

    def test_bfs_path_simple(self):
        config = Config(width=10, height=10)
        board = Board(config)

        path = bfs_path(Position(0, 0), Position(3, 0), board, set())
        assert path is not None
        assert len(path) == 3
        assert all(d == Direction.RIGHT for d in path)

    def test_bfs_path_with_obstacles(self):
        config = Config(width=10, height=10)
        board = Board(config)

        # Create a wall between start and target
        board.cells[0][1].cell_type = CellType.WALL
        board.cells[1][1].cell_type = CellType.WALL

        path = bfs_path(Position(0, 0), Position(2, 0), board, set())
        assert path is not None
        # Path should go around the wall
        assert len(path) > 2

    def test_bfs_path_no_path(self):
        config = Config(width=5, height=5)
        board = Board(config)

        # Completely block off the target
        for y in range(5):
            board.cells[y][2].cell_type = CellType.WALL

        path = bfs_path(Position(0, 0), Position(4, 0), board, set())
        assert path is None

    def test_bfs_path_same_position(self):
        config = Config(width=10, height=10)
        board = Board(config)

        path = bfs_path(Position(5, 5), Position(5, 5), board, set())
        assert path == []

    def test_find_safe_moves(self):
        config = Config(width=10, height=10)
        board = Board(config)
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)

        safe_moves = find_safe_moves(snake, board)

        # Should not include LEFT (reverse direction)
        assert Direction.LEFT not in safe_moves
        # Should include forward and perpendicular
        assert Direction.RIGHT in safe_moves
        assert Direction.UP in safe_moves
        assert Direction.DOWN in safe_moves

    def test_find_safe_moves_near_wall(self):
        config = Config(width=10, height=10)
        board = Board(config)

        # Create a wall to the right of the snake head
        board.cells[5][6].cell_type = CellType.WALL

        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        safe_moves = find_safe_moves(snake, board)

        # RIGHT should not be safe due to wall
        assert Direction.RIGHT not in safe_moves

    def test_find_safe_moves_corner(self):
        config = Config(width=10, height=10)
        board = Board(config)
        snake = Snake.create(Position(0, 0), length=1, direction=Direction.RIGHT)

        safe_moves = find_safe_moves(snake, board)

        # UP and LEFT should not be safe (boundary)
        assert Direction.UP not in safe_moves
        assert Direction.LEFT not in safe_moves
        # DOWN and RIGHT should be safe
        assert Direction.DOWN in safe_moves
        assert Direction.RIGHT in safe_moves

    def test_evaluate_move_safety(self):
        config = Config(width=10, height=10)
        board = Board(config)
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)

        # All directions should have decent space
        right_space = evaluate_move_safety(snake, Direction.RIGHT, board)
        up_space = evaluate_move_safety(snake, Direction.UP, board)

        assert right_space > 0
        assert up_space > 0


class TestAIController:
    """Tests for AIController class."""

    def test_ai_greedy_strategy(self):
        config = Config(
            width=20,
            height=10,
            seed=42,
            ai_strategy="greedy",
            contribution_mode="walls",
        )
        engine = GameEngine(config)
        engine.setup()
        ai = AIController(config)

        # Should return a valid direction
        direction = ai.get_next_direction(engine.get_state())
        assert isinstance(direction, Direction)

    def test_ai_bfs_safe_strategy(self):
        config = Config(
            width=20,
            height=10,
            seed=42,
            ai_strategy="bfs_safe",
            contribution_mode="walls",
        )
        engine = GameEngine(config)
        engine.setup()
        ai = AIController(config)

        direction = ai.get_next_direction(engine.get_state())
        assert isinstance(direction, Direction)

    def test_ai_survival_strategy(self):
        config = Config(
            width=20,
            height=10,
            seed=42,
            ai_strategy="survival",
            contribution_mode="walls",
        )
        engine = GameEngine(config)
        engine.setup()
        ai = AIController(config)

        direction = ai.get_next_direction(engine.get_state())
        assert isinstance(direction, Direction)

    def test_ai_commit_hunter_prefers_continuing_direction_on_tie(self):
        config = Config(
            width=7,
            height=7,
            seed=42,
            ai_strategy="commit_hunter",
            contribution_mode="food",
        )
        board = Board(config)
        board.cells[3][4].contribution_level = 2  # RIGHT
        board.cells[2][3].contribution_level = 2  # UP (same distance)

        snake = Snake.create(Position(3, 3), length=1, direction=Direction.RIGHT)
        state = GameState(
            board=board,
            snake=snake,
            food=Position(4, 3),
            score=0,
            tick=0,
            status="running",
        )

        ai = AIController(config)
        direction = ai.get_next_direction(state)
        assert direction == Direction.RIGHT

    def test_ai_commit_hunter_falls_back_to_survival_when_targets_blocked(self):
        config = Config(
            width=5,
            height=5,
            seed=42,
            ai_strategy="commit_hunter",
            contribution_mode="food",
        )
        board = Board(config)
        board.cells[4][4].contribution_level = 4

        # Force only one safe move (DOWN).
        board.cells[1][0].cell_type = CellType.WALL
        board.cells[0][1].cell_type = CellType.WALL
        board.cells[1][2].cell_type = CellType.WALL

        snake = Snake.create(Position(1, 1), length=1, direction=Direction.RIGHT)
        state = GameState(
            board=board,
            snake=snake,
            food=Position(4, 4),
            score=0,
            tick=0,
            status="running",
        )

        ai = AIController(config)
        direction = ai.get_next_direction(state)
        assert direction == Direction.DOWN

    def test_ai_plays_game(self):
        config = Config(
            width=15,
            height=10,
            seed=42,
            max_ticks=100,
            contribution_mode="walls",
        )
        engine = GameEngine(config)
        engine.setup()
        ai = AIController(config)

        # Let AI play for a while
        while engine.is_running() and engine.tick < 50:
            direction = ai.get_next_direction(engine.get_state())
            engine.step(direction)

        # Game should have progressed
        assert engine.tick > 0

    def test_ai_no_safe_moves_fallback(self):
        """Test that AI handles situations with no safe moves gracefully."""
        config = Config(width=5, height=5, seed=42)
        board = Board(config)

        # Create a very confined space
        for x in range(5):
            board.cells[0][x].cell_type = CellType.WALL
            board.cells[4][x].cell_type = CellType.WALL
        for y in range(5):
            board.cells[y][0].cell_type = CellType.WALL
            board.cells[y][4].cell_type = CellType.WALL

        # Snake in the confined space
        snake = Snake.create(Position(2, 2), length=1, direction=Direction.RIGHT)

        ai = AIController(config)

        # Create a minimal game state
        state = GameState(
            board=board,
            snake=snake,
            food=Position(3, 2),
            score=0,
            tick=0,
            status="running",
        )

        # AI should return some direction without crashing
        direction = ai.get_next_direction(state)
        assert isinstance(direction, Direction)
