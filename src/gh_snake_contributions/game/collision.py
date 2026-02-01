"""Collision detection for the Snake game."""

from dataclasses import dataclass
from enum import Enum, auto

from .board import Board, Position
from .snake import Snake


class CollisionType(Enum):
    """Types of collisions that can occur."""

    NONE = auto()
    WALL = auto()
    BOUNDARY = auto()
    SELF = auto()


@dataclass
class CollisionDetector:
    """Detects collisions between game entities."""

    board: Board

    def check_snake_collision(self, snake: Snake) -> CollisionType:
        """Check if the snake has collided with anything.

        Args:
            snake: The snake to check.

        Returns:
            The type of collision, or NONE if no collision.
        """
        head = snake.head

        # Check boundary collision
        if not self.board.is_valid_position(head):
            return CollisionType.BOUNDARY

        # Check wall collision
        if not self.board.is_walkable(head):
            return CollisionType.WALL

        # Check self collision
        if snake.collides_with_self():
            return CollisionType.SELF

        return CollisionType.NONE

    def would_collide(self, snake: Snake, position: Position) -> CollisionType:
        """Check if moving to a position would cause a collision.

        Args:
            snake: The snake to check.
            position: The position to check.

        Returns:
            The type of collision that would occur.
        """
        # Check boundary
        if not self.board.is_valid_position(position):
            return CollisionType.BOUNDARY

        # Check wall
        if not self.board.is_walkable(position):
            return CollisionType.WALL

        # Check self collision
        # When moving, the tail will move unless the snake is growing
        body_positions = set(list(snake.body)[:-1])  # Exclude tail (it will move)
        if snake.growing:
            body_positions.add(snake.tail)

        if position in body_positions:
            return CollisionType.SELF

        return CollisionType.NONE

    def check_food_collision(self, snake: Snake, food: Position | None) -> bool:
        """Check if the snake head is on food.

        Args:
            snake: The snake to check.
            food: The food position, or None.

        Returns:
            True if the snake head is on the food.
        """
        if food is None:
            return False
        return snake.head == food
