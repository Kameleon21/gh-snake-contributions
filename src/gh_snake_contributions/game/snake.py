"""Snake entity implementation."""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from .board import Position


class Direction(Enum):
    """Movement directions for the snake."""

    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)

    @property
    def opposite(self) -> "Direction":
        """Get the opposite direction."""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]


@dataclass
class Snake:
    """Represents the snake entity."""

    # Body segments, head is at index 0
    body: deque[Position] = field(default_factory=deque)
    direction: Direction = Direction.RIGHT
    growing: bool = False

    @property
    def head(self) -> Position:
        """Get the head position."""
        return self.body[0]

    @property
    def tail(self) -> Position:
        """Get the tail position."""
        return self.body[-1]

    @property
    def length(self) -> int:
        """Get the current length of the snake."""
        return len(self.body)

    def get_body_positions(self) -> set[Position]:
        """Get all body positions as a set."""
        return set(self.body)

    def get_next_head_position(self, direction: Direction | None = None) -> Position:
        """Calculate where the head will be after moving.

        Args:
            direction: Direction to move. Uses current direction if None.

        Returns:
            The next head position.
        """
        if direction is None:
            direction = self.direction
        return self.head + direction.value

    def move(self, direction: Direction | None = None) -> None:
        """Move the snake in the given direction.

        Args:
            direction: Direction to move. Uses current direction if None.
        """
        if direction is not None:
            # Prevent reversing into self
            if direction != self.direction.opposite or self.length == 1:
                self.direction = direction

        new_head = self.get_next_head_position()
        self.body.appendleft(new_head)

        if self.growing:
            self.growing = False
        else:
            self.body.pop()

    def grow(self) -> None:
        """Mark the snake to grow on next move."""
        self.growing = True

    def collides_with_self(self) -> bool:
        """Check if the head collides with any body segment."""
        body_set = set(list(self.body)[1:])  # Exclude head
        return self.head in body_set

    @classmethod
    def create(
        cls,
        start_position: Position,
        length: int = 3,
        direction: Direction = Direction.RIGHT,
    ) -> "Snake":
        """Create a new snake at the given position.

        Args:
            start_position: Position for the head.
            length: Initial length of the snake.
            direction: Initial direction.

        Returns:
            A new Snake instance.
        """
        body: deque[Position] = deque()

        # Create body segments extending opposite to direction
        opposite = direction.opposite.value
        for i in range(length):
            body.append(Position(start_position.x + opposite.x * i, start_position.y + opposite.y * i))

        return cls(body=body, direction=direction)
