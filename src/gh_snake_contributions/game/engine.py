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
    show_snake: bool = True
    show_food: bool = True


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
        self._food_spawner = FoodSpawner(
            self.board,
            self.config.get_rng(),
            mode=self.config.contribution_mode,
        )

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

        # Reset game state
        self.score = 0
        self.tick = 0
        self.status = "running"

        # Spawn initial food
        self.food = self._food_spawner.spawn(self.snake.get_body_positions())

        if (
            self.config.contribution_mode == "food"
            and self.food is None
            and self.board.count_contribution_cells() == 0
        ):
            self.status = "won"

    def _find_start_position(self) -> Position:
        """Find a valid starting position for the snake.

        Returns:
            A position where the snake can start.
        """
        preferred = self.config.spawn_position
        fallback_order = ["bottom_center", "center", "legacy_left"]

        strategies = [preferred]
        for strategy in fallback_order:
            if strategy not in strategies:
                strategies.append(strategy)

        for strategy in strategies:
            for pos in self._spawn_candidates(strategy):
                if self._is_valid_spawn(pos):
                    return pos

        # Fallback: find any valid position
        empty = self.board.get_empty_positions()
        if empty:
            rng = self.config.get_rng()
            return rng.choice(empty)

        # Last resort: center of board
        return Position(self.board.width // 2, self.board.height // 2)

    def _is_valid_spawn(self, head_pos: Position) -> bool:
        """Check if the full initial snake body fits from a head position."""
        for i in range(self.config.initial_length):
            check_pos = Position(head_pos.x - i, head_pos.y)
            if not self.board.is_walkable(check_pos):
                return False
        return True

    def _spawn_candidates(self, strategy: str) -> list[Position]:
        """Generate head-position candidates for a spawn strategy."""
        x_min = self.config.initial_length - 1
        x_max = self.board.width - 1
        if x_min > x_max:
            return []

        if strategy == "lower_half_random":
            y_start = self.board.height // 2
            candidates = [
                Position(x, y)
                for y in range(y_start, self.board.height)
                for x in range(x_min, x_max + 1)
            ]
            self.config.get_rng().shuffle(candidates)
            return candidates

        if strategy == "bottom_center":
            anchor = Position(self.board.width // 2, self.board.height - 1)
            return self._radial_candidates(anchor, x_min, x_max)

        if strategy == "center":
            anchor = Position(self.board.width // 2, self.board.height // 2)
            return self._radial_candidates(anchor, x_min, x_max)

        # legacy_left strategy
        candidates: list[Position] = []
        for y in range(self.board.height // 2 - 2, self.board.height // 2 + 3):
            if y < 0 or y >= self.board.height:
                continue
            for x in range(self.config.initial_length + 1, self.board.width // 3):
                if x_min <= x <= x_max:
                    candidates.append(Position(x, y))
        return candidates

    def _radial_candidates(self, anchor: Position, x_min: int, x_max: int) -> list[Position]:
        """Return board positions sorted by distance to anchor."""
        candidates = [
            Position(x, y)
            for y in range(self.board.height)
            for x in range(x_min, x_max + 1)
        ]
        candidates.sort(
            key=lambda pos: (
                abs(pos.x - anchor.x) + abs(pos.y - anchor.y),
                abs(pos.y - anchor.y),
                abs(pos.x - anchor.x),
            )
        )
        return candidates

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

        # Check for food / commit consumption
        if self.config.contribution_mode == "food":
            # In food mode, any contribution cell the snake visits is consumed.
            consumed = self.board.consume_contribution(self.snake.head)
            if consumed:
                self.snake.grow()
                self.score += 1
                if self.food == self.snake.head:
                    self.food = None
        elif self._collision_detector.check_food_collision(self.snake, self.food):
            self.snake.grow()
            self.score += 1
            self.food = None

        # Spawn new food if needed
        self.food = self._food_spawner.spawn_if_needed(
            self.food,
            self.snake.get_body_positions(),
        )

        if (
            self.config.contribution_mode == "food"
            and self.food is None
            and self.board.count_contribution_cells() == 0
        ):
            self.status = "won"
            return self.get_state()

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
