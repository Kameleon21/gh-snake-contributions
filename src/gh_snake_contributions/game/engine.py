"""Main game engine orchestrating the Snake game simulation."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from .board import Board, Position
from .collision import CollisionDetector, CollisionType
from .food import FoodSpawner
from .snake import Direction, Snake

if TYPE_CHECKING:
    from ..config import Config


GameStatus = Literal["running", "won", "collision", "timeout"]


@dataclass
class GameState:
    """Represents the complete state of the game."""

    board: Board
    snake: Snake
    food: Position | None
    score: int
    tick: int
    status: GameStatus


@dataclass
class GameEngine:
    """Main game engine that runs the simulation."""

    config: "Config"
    board: Board = field(init=False)
    snake: Snake = field(init=False)
    food: Position | None = field(init=False, default=None)
    score: int = field(init=False, default=0)
    tick: int = field(init=False, default=0)
    status: GameStatus = field(init=False, default="running")

    _collision_detector: CollisionDetector = field(init=False)
    _food_spawner: FoodSpawner = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the game components."""
        self.board = Board(self.config)
        self._collision_detector = CollisionDetector(self.board)
        self._food_spawner = FoodSpawner(self.board, self.config.get_rng())

    def setup(self, contributions: list[list[int]] | None = None) -> None:
        """Set up the game with optional contribution data.

        Args:
            contributions: 2D list of contribution levels (0-4).
        """
        # Apply contributions to board
        if contributions:
            self.board.apply_contributions(contributions)

        # Find a valid starting position for the snake
        start_pos = self._find_start_position()
        self.snake = Snake.create(
            start_position=start_pos,
            length=self.config.initial_length,
            direction=Direction.RIGHT,
        )

        # Spawn initial food
        self.food = self._food_spawner.spawn(self.snake.get_body_positions())

        # Reset game state
        self.score = 0
        self.tick = 0
        self.status = "running"

    def _find_start_position(self) -> Position:
        """Find a valid starting position for the snake.

        Returns:
            A position where the snake can start.
        """
        # Try to start near the left side with room for initial length
        for y in range(self.board.height // 2 - 2, self.board.height // 2 + 3):
            for x in range(self.config.initial_length + 1, self.board.width // 3):
                # Check if there's room for the snake
                pos = Position(x, y)
                valid = True
                for i in range(self.config.initial_length):
                    check_pos = Position(x - i, y)
                    if not self.board.is_walkable(check_pos):
                        valid = False
                        break
                if valid:
                    return pos

        # Fallback: find any valid position
        empty = self.board.get_empty_positions()
        if empty:
            rng = self.config.get_rng()
            return rng.choice(empty)

        # Last resort: center of board
        return Position(self.board.width // 2, self.board.height // 2)

    def get_state(self) -> GameState:
        """Get the current game state.

        Returns:
            A snapshot of the current game state.
        """
        return GameState(
            board=self.board,
            snake=self.snake,
            food=self.food,
            score=self.score,
            tick=self.tick,
            status=self.status,
        )

    def step(self, direction: Direction | None = None) -> GameState:
        """Execute one game tick.

        Args:
            direction: Direction to move the snake. Uses current direction if None.

        Returns:
            The game state after the step.
        """
        if self.status != "running":
            return self.get_state()

        # Move the snake
        self.snake.move(direction)
        self.tick += 1

        # Check for collisions
        collision = self._collision_detector.check_snake_collision(self.snake)
        if collision != CollisionType.NONE:
            self.status = "collision"
            return self.get_state()

        # Check for food
        if self._collision_detector.check_food_collision(self.snake, self.food):
            self.snake.grow()
            self.score += 1
            self.food = None

        # Spawn new food if needed
        self.food = self._food_spawner.spawn_if_needed(
            self.food,
            self.snake.get_body_positions(),
        )

        # Check for win condition (no more empty cells)
        if self.food is None:
            empty = self.board.get_empty_positions(exclude=self.snake.get_body_positions())
            if not empty:
                self.status = "won"
                return self.get_state()

        # Check for timeout
        if self.tick >= self.config.max_ticks:
            self.status = "timeout"

        return self.get_state()

    def is_running(self) -> bool:
        """Check if the game is still running.

        Returns:
            True if the game is still running.
        """
        return self.status == "running"
