"""Board setup and contribution mapping."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Config


class CellType(Enum):
    """Types of cells on the game board."""

    EMPTY = 0
    WALL = 1


@dataclass
class Cell:
    """Represents a single cell on the board."""

    cell_type: CellType
    contribution_level: int = 0  # 0-4 scale from GitHub


@dataclass(frozen=True)
class Position:
    """Represents a position on the board."""

    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)


class Board:
    """Game board with contribution mapping."""

    def __init__(self, config: "Config") -> None:
        self.width = config.width
        self.height = config.height
        self.config = config
        self.cells: list[list[Cell]] = [
            [Cell(CellType.EMPTY) for _ in range(config.width)]
            for _ in range(config.height)
        ]

    def apply_contributions(self, contributions: list[list[int]]) -> None:
        """Apply contribution data to the board.

        Args:
            contributions: 2D list of contribution levels (0-4 scale).
                          Will be normalized to fit the board dimensions.
        """
        if not contributions or not contributions[0]:
            return

        # GitHub provides 52 weeks × 7 days = 52×7 grid
        # We need to map it to our board dimensions
        src_height = len(contributions)
        src_width = len(contributions[0])

        for y in range(self.height):
            for x in range(self.width):
                # Map board coordinates to contribution coordinates
                src_x = int(x * src_width / self.width)
                src_y = int(y * src_height / self.height)

                # Clamp to valid indices
                src_x = min(src_x, src_width - 1)
                src_y = min(src_y, src_height - 1)

                level = contributions[src_y][src_x]
                self.cells[y][x].contribution_level = level

                if self.config.contribution_mode == "walls":
                    if level >= self.config.wall_threshold:
                        self.cells[y][x].cell_type = CellType.WALL

    def is_valid_position(self, pos: Position) -> bool:
        """Check if a position is within board boundaries."""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_walkable(self, pos: Position) -> bool:
        """Check if a position can be walked on (valid and not a wall)."""
        if not self.is_valid_position(pos):
            return False
        return self.cells[pos.y][pos.x].cell_type != CellType.WALL

    def get_cell(self, pos: Position) -> Cell | None:
        """Get the cell at a position, or None if out of bounds."""
        if not self.is_valid_position(pos):
            return None
        return self.cells[pos.y][pos.x]

    def get_empty_positions(self, exclude: set[Position] | None = None) -> list[Position]:
        """Get all empty positions on the board.

        Args:
            exclude: Positions to exclude (e.g., snake body).

        Returns:
            List of empty positions.
        """
        exclude = exclude or set()
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                pos = Position(x, y)
                if self.is_walkable(pos) and pos not in exclude:
                    positions.append(pos)
        return positions
