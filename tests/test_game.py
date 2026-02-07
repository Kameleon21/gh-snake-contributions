"""Tests for game engine components."""

import pytest

from gh_snake_contributions.ai.controller import AIController
from gh_snake_contributions.config import Config
from gh_snake_contributions.game.board import Board, CellType, Position
from gh_snake_contributions.game.collision import CollisionDetector, CollisionType
from gh_snake_contributions.game.engine import GameEngine
from gh_snake_contributions.game.food import FoodSpawner
from gh_snake_contributions.game.snake import Direction, Snake


class TestPosition:
    """Tests for Position class."""

    def test_position_creation(self):
        pos = Position(5, 10)
        assert pos.x == 5
        assert pos.y == 10

    def test_position_addition(self):
        pos1 = Position(3, 4)
        pos2 = Position(1, 2)
        result = pos1 + pos2
        assert result.x == 4
        assert result.y == 6

    def test_position_equality(self):
        pos1 = Position(5, 5)
        pos2 = Position(5, 5)
        pos3 = Position(5, 6)
        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_hashable(self):
        pos1 = Position(5, 5)
        pos2 = Position(5, 5)
        positions = {pos1, pos2}
        assert len(positions) == 1


class TestDirection:
    """Tests for Direction enum."""

    def test_direction_values(self):
        assert Direction.UP.value == Position(0, -1)
        assert Direction.DOWN.value == Position(0, 1)
        assert Direction.LEFT.value == Position(-1, 0)
        assert Direction.RIGHT.value == Position(1, 0)

    def test_direction_opposite(self):
        assert Direction.UP.opposite == Direction.DOWN
        assert Direction.DOWN.opposite == Direction.UP
        assert Direction.LEFT.opposite == Direction.RIGHT
        assert Direction.RIGHT.opposite == Direction.LEFT


class TestSnake:
    """Tests for Snake class."""

    def test_snake_creation(self):
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        assert snake.length == 3
        assert snake.head == Position(5, 5)
        assert snake.direction == Direction.RIGHT

    def test_snake_move(self):
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        snake.move()
        assert snake.head == Position(6, 5)
        assert snake.length == 3

    def test_snake_grow(self):
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        snake.grow()
        snake.move()
        assert snake.length == 4

    def test_snake_no_reverse(self):
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        snake.move(Direction.LEFT)  # Try to reverse
        assert snake.direction == Direction.RIGHT  # Should not reverse

    def test_snake_collides_with_self(self):
        snake = Snake.create(Position(5, 5), length=5, direction=Direction.RIGHT)
        # Move in a way that would cause self-collision
        snake.move(Direction.RIGHT)
        snake.move(Direction.DOWN)
        snake.move(Direction.LEFT)
        snake.move(Direction.UP)  # This should collide with body
        assert snake.collides_with_self()


class TestBoard:
    """Tests for Board class."""

    def test_board_creation(self):
        config = Config(width=10, height=10)
        board = Board(config)
        assert board.width == 10
        assert board.height == 10

    def test_board_valid_position(self):
        config = Config(width=10, height=10)
        board = Board(config)
        assert board.is_valid_position(Position(0, 0))
        assert board.is_valid_position(Position(9, 9))
        assert not board.is_valid_position(Position(-1, 0))
        assert not board.is_valid_position(Position(10, 0))

    def test_board_apply_contributions(self):
        config = Config(width=10, height=7, wall_threshold=3, contribution_mode="walls")
        board = Board(config)

        # Simple contributions with some high values
        contributions = [
            [0, 1, 2, 3, 4, 3, 2, 1, 0, 1],
            [1, 2, 3, 4, 3, 2, 1, 0, 1, 2],
            [2, 3, 4, 3, 2, 1, 0, 1, 2, 3],
            [3, 4, 3, 2, 1, 0, 1, 2, 3, 4],
            [4, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            [3, 2, 1, 0, 1, 2, 3, 4, 3, 2],
            [2, 1, 0, 1, 2, 3, 4, 3, 2, 1],
        ]
        board.apply_contributions(contributions)

        # Check that walls were created for high contribution cells
        wall_count = sum(
            1 for y in range(board.height) for x in range(board.width)
            if board.cells[y][x].cell_type == CellType.WALL
        )
        assert wall_count > 0

    def test_board_walkable(self):
        config = Config(width=10, height=10)
        board = Board(config)

        # Empty cell should be walkable
        assert board.is_walkable(Position(5, 5))

        # Make a cell a wall
        board.cells[5][5].cell_type = CellType.WALL
        assert not board.is_walkable(Position(5, 5))

    def test_board_contribution_positions_and_consume(self):
        config = Config(width=4, height=3)
        board = Board(config)
        board.cells[0][1].contribution_level = 2
        board.cells[2][3].contribution_level = 4

        positions = board.get_contribution_positions()
        assert Position(1, 0) in positions
        assert Position(3, 2) in positions
        assert board.count_contribution_cells() == 2

        assert board.consume_contribution(Position(1, 0))
        assert board.cells[0][1].contribution_level == 0
        assert board.count_contribution_cells() == 1


class TestCollisionDetector:
    """Tests for CollisionDetector class."""

    def test_no_collision(self):
        config = Config(width=10, height=10)
        board = Board(config)
        detector = CollisionDetector(board)
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)

        assert detector.check_snake_collision(snake) == CollisionType.NONE

    def test_boundary_collision(self):
        config = Config(width=10, height=10)
        board = Board(config)
        detector = CollisionDetector(board)
        snake = Snake.create(Position(9, 5), length=3, direction=Direction.RIGHT)
        snake.move()  # Move out of bounds

        assert detector.check_snake_collision(snake) == CollisionType.BOUNDARY

    def test_wall_collision(self):
        config = Config(width=10, height=10)
        board = Board(config)
        board.cells[5][6].cell_type = CellType.WALL
        detector = CollisionDetector(board)
        snake = Snake.create(Position(5, 5), length=3, direction=Direction.RIGHT)
        snake.move()  # Move into wall

        assert detector.check_snake_collision(snake) == CollisionType.WALL


class TestFoodSpawner:
    """Tests for FoodSpawner class."""

    def test_food_spawn(self):
        import random
        config = Config(width=10, height=10, seed=42)
        board = Board(config)
        spawner = FoodSpawner(board, config.get_rng())

        food = spawner.spawn(set())
        assert food is not None
        assert board.is_valid_position(food)

    def test_food_spawn_avoids_occupied(self):
        import random
        config = Config(width=3, height=3, seed=42)
        board = Board(config)
        spawner = FoodSpawner(board, config.get_rng())

        # Occupy most of the board
        occupied = {Position(x, y) for x in range(3) for y in range(2)}

        food = spawner.spawn(occupied)
        assert food is not None
        assert food not in occupied

    def test_food_mode_spawns_only_on_contribution_cells(self):
        config = Config(width=4, height=4, seed=42, contribution_mode="food")
        board = Board(config)
        board.cells[0][1].contribution_level = 1
        board.cells[2][3].contribution_level = 4
        spawner = FoodSpawner(board, config.get_rng(), mode="food")

        for _ in range(10):
            food = spawner.spawn(set())
            assert food in {Position(1, 0), Position(3, 2)}

    def test_food_mode_returns_none_when_no_contributions_left(self):
        config = Config(width=4, height=4, seed=42, contribution_mode="food")
        board = Board(config)
        spawner = FoodSpawner(board, config.get_rng(), mode="food")

        food = spawner.spawn(set())
        assert food is None


class TestGameEngine:
    """Tests for GameEngine class."""

    def test_engine_setup(self):
        config = Config(width=20, height=10, seed=42, contribution_mode="walls")
        engine = GameEngine(config)
        engine.setup()

        assert engine.is_running()
        assert engine.snake is not None
        assert engine.food is not None

    def test_engine_step(self):
        config = Config(width=20, height=10, seed=42, contribution_mode="walls")
        engine = GameEngine(config)
        engine.setup()

        initial_tick = engine.tick
        engine.step()

        assert engine.tick == initial_tick + 1

    def test_engine_collision_ends_game(self):
        config = Config(width=5, height=5, seed=42, contribution_mode="walls")
        engine = GameEngine(config)
        engine.setup()

        # Keep moving right until collision with boundary
        while engine.is_running():
            engine.step(Direction.RIGHT)

        assert engine.status == "collision"

    def test_engine_with_contributions(self):
        config = Config(
            width=10,
            height=7,
            seed=42,
            wall_threshold=4,
            contribution_mode="walls",
        )
        engine = GameEngine(config)

        contributions = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        engine.setup(contributions)

        assert engine.is_running()

    def test_engine_food_mode_consumes_contribution_cell(self):
        config = Config(width=10, height=7, seed=42, contribution_mode="food")
        engine = GameEngine(config)
        contributions = [[1 for _ in range(10)] for _ in range(7)]
        engine.setup(contributions)

        target = engine.snake.head + Direction.RIGHT.value
        assert engine.board.is_walkable(target)

        engine.board.cells[target.y][target.x].contribution_level = 3
        engine.food = target

        engine.step(Direction.RIGHT)

        assert engine.score == 1
        assert engine.board.cells[target.y][target.x].contribution_level == 0

    def test_engine_food_mode_consumes_non_target_contribution_cell(self):
        config = Config(width=10, height=7, seed=42, contribution_mode="food")
        engine = GameEngine(config)
        contributions = [[1 for _ in range(10)] for _ in range(7)]
        engine.setup(contributions)

        head = engine.snake.head
        step_direction = None
        for candidate in (Direction.RIGHT, Direction.DOWN, Direction.UP):
            candidate_pos = head + candidate.value
            if engine.board.is_walkable(candidate_pos):
                step_direction = candidate
                next_pos = candidate_pos
                break

        assert step_direction is not None

        food_pos = None
        for candidate in (Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT):
            candidate_pos = head + candidate.value
            if candidate_pos != next_pos and engine.board.is_walkable(candidate_pos):
                food_pos = candidate_pos
                break

        assert engine.board.is_walkable(next_pos)
        assert food_pos is not None

        engine.board.cells[next_pos.y][next_pos.x].contribution_level = 2
        engine.board.cells[food_pos.y][food_pos.x].contribution_level = 3
        engine.food = food_pos

        engine.step(step_direction)

        assert engine.score == 1
        assert engine.board.cells[next_pos.y][next_pos.x].contribution_level == 0
        assert engine.food == food_pos

    def test_engine_spawn_lower_half_random(self):
        config = Config(
            width=20,
            height=10,
            seed=42,
            contribution_mode="walls",
            spawn_position="lower_half_random",
        )
        engine = GameEngine(config)
        engine.setup()

        assert engine.snake.head.y >= config.height // 2
        for pos in engine.snake.body:
            assert engine.board.is_walkable(pos)

    def test_engine_pacing_moves_slower_than_frames(self):
        config = Config(
            width=30,
            height=12,
            seed=42,
            contribution_mode="walls",
            ai_strategy="survival",
            fps=12,
            moves_per_second=8.0,
            max_duration=2.0,
        )
        engine = GameEngine(config)
        engine.setup()
        ai = AIController(config)

        frame_count = 0
        move_budget = 0.0
        max_frames = config.max_frames

        while engine.is_running() and frame_count < max_frames:
            move_budget += config.moves_per_second / config.fps
            while move_budget >= 1.0 and engine.is_running():
                direction = ai.get_next_direction(engine.get_state())
                engine.step(direction)
                move_budget -= 1.0
            frame_count += 1

        expected_ticks = int(frame_count * config.moves_per_second / config.fps)
        assert engine.tick < frame_count
        assert abs(engine.tick - expected_ticks) <= 1
