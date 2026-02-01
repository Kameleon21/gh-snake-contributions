"""Food spawning logic."""

import random
from dataclasses import dataclass

from .board import Board, Position


@dataclass
class FoodSpawner:
    """Handles food placement on the board."""

    board: Board
    rng: random.Random

    def spawn(self, occupied: set[Position]) -> Position | None:
        """Spawn food at a random empty position.

        Args:
            occupied: Set of positions that are occupied (e.g., by snake).

        Returns:
            The position where food was spawned, or None if no space.
        """
        empty_positions = self.board.get_empty_positions(exclude=occupied)

        if not empty_positions:
            return None

        return self.rng.choice(empty_positions)

    def spawn_if_needed(
        self,
        current_food: Position | None,
        occupied: set[Position],
    ) -> Position | None:
        """Spawn food if there is none currently.

        Args:
            current_food: Current food position, or None.
            occupied: Set of occupied positions.

        Returns:
            The food position (existing or new), or None if no space.
        """
        if current_food is not None:
            return current_food
        return self.spawn(occupied)
