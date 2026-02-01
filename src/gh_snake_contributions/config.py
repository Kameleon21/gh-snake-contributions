"""Configuration management for the Snake game."""

from dataclasses import dataclass, field
from typing import Literal
import hashlib
import random


@dataclass
class Config:
    """Configuration for the Snake game."""

    # Board settings
    width: int = 30
    height: int = 15
    cell_size: int = 16
    contribution_mode: Literal["walls", "food", "speed"] = "walls"
    wall_threshold: int = 3  # Contribution level 3+ becomes wall (0-4 scale)

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
    theme_mode: Literal["auto", "force", "disable"] = "auto"
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
