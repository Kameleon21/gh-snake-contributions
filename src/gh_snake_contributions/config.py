"""Configuration management for the Snake game."""

from dataclasses import dataclass, field
from typing import Literal
import hashlib
import random


@dataclass
class Config:
    """Configuration for the Snake game."""

    # Board settings
    width: int = 52  # Matches GitHub's 52 weeks
    height: int = 7  # Matches GitHub's 7 days
    cell_size: int = 15  # 52*15 = 780px width, fits README
    contribution_mode: Literal["walls", "food", "speed"] = "walls"
    wall_threshold: int = 5  # No walls by default (max contribution is 4)

    # Game settings
    initial_length: int = 3
    max_ticks: int = 500

    # AI settings
    ai_strategy: Literal["greedy", "bfs_safe", "survival"] = "bfs_safe"

    # GIF settings
    fps: int = 12
    max_duration: float = 8.0
    output_path: str = "snake.gif"

    # Theme settings
    theme_mode: Literal["auto", "force", "disable"] = "disable"  # Use default green theme
    forced_theme: str | None = None

    # Determinism
    seed: int | str | None = None

    # Internal
    _rng: random.Random = field(default_factory=random.Random, repr=False)

    def __post_init__(self) -> None:
        """Initialize the random number generator with the seed."""
        if self.seed is not None:
            if isinstance(self.seed, str):
                # Convert string seed to int using hash
                seed_int = int(hashlib.sha256(self.seed.encode()).hexdigest(), 16) % (2**32)
            else:
                seed_int = self.seed
            self._rng = random.Random(seed_int)
        else:
            self._rng = random.Random()

    @property
    def max_frames(self) -> int:
        """Calculate maximum number of frames based on FPS and duration."""
        return int(self.fps * self.max_duration)

    @property
    def frame_duration_ms(self) -> int:
        """Calculate frame duration in milliseconds."""
        return int(1000 / self.fps)

    def get_rng(self) -> random.Random:
        """Get the seeded random number generator."""
        return self._rng
