"""Seasonal color themes for the Snake game."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

ThemeName = Literal["default", "halloween", "winter", "spring", "summer", "space"]


@dataclass(frozen=True)
class Theme:
    """Color theme for rendering."""

    name: str

    # Background
    background: tuple[int, int, int]

    # Grid
    grid_line: tuple[int, int, int]

    # Contribution levels (0-4)
    contribution_0: tuple[int, int, int]  # No contributions
    contribution_1: tuple[int, int, int]  # Low
    contribution_2: tuple[int, int, int]  # Medium-low
    contribution_3: tuple[int, int, int]  # Medium-high
    contribution_4: tuple[int, int, int]  # High

    # Snake
    snake_head: tuple[int, int, int]
    snake_body: tuple[int, int, int]
    snake_tail: tuple[int, int, int]

    # Food
    food: tuple[int, int, int]

    # Walls (high contribution in wall mode)
    wall: tuple[int, int, int]

    # HUD / Text
    text: tuple[int, int, int]

    def get_contribution_color(self, level: int) -> tuple[int, int, int]:
        """Get the color for a contribution level.

        Args:
            level: Contribution level (0-4).

        Returns:
            RGB color tuple.
        """
        colors = [
            self.contribution_0,
            self.contribution_1,
            self.contribution_2,
            self.contribution_3,
            self.contribution_4,
        ]
        return colors[min(level, 4)]


# Default GitHub-style green theme
DEFAULT_THEME = Theme(
    name="default",
    background=(13, 17, 23),  # GitHub dark background
    grid_line=(33, 38, 45),
    contribution_0=(22, 27, 34),  # ebedf0 dark equivalent
    contribution_1=(14, 68, 41),  # 9be9a8 dark
    contribution_2=(0, 109, 50),  # 40c463
    contribution_3=(38, 166, 65),  # 30a14e
    contribution_4=(57, 211, 83),  # 216e39
    snake_head=(57, 211, 83),  # Bright green head (matches contribution_4)
    snake_body=(38, 166, 65),  # Medium green body
    snake_tail=(0, 109, 50),  # Darker green tail
    food=(255, 123, 114),  # Red food
    wall=(55, 62, 71),  # Darker gray walls - more distinct
    text=(201, 209, 217),
)

# Halloween theme (October)
HALLOWEEN_THEME = Theme(
    name="halloween",
    background=(20, 15, 25),
    grid_line=(40, 30, 50),
    contribution_0=(30, 25, 35),
    contribution_1=(80, 40, 20),
    contribution_2=(120, 60, 20),
    contribution_3=(180, 90, 20),
    contribution_4=(255, 140, 0),  # Orange
    snake_head=(148, 0, 211),  # Purple head
    snake_body=(138, 43, 226),
    snake_tail=(128, 0, 128),
    food=(255, 215, 0),  # Gold food
    wall=(60, 50, 70),
    text=(255, 200, 100),
)

# Winter theme (December-February)
WINTER_THEME = Theme(
    name="winter",
    background=(15, 25, 40),
    grid_line=(30, 50, 70),
    contribution_0=(25, 35, 50),
    contribution_1=(50, 100, 150),
    contribution_2=(80, 140, 200),
    contribution_3=(120, 180, 230),
    contribution_4=(200, 230, 255),  # Light blue/white
    snake_head=(100, 200, 255),  # Ice blue head
    snake_body=(70, 170, 230),
    snake_tail=(50, 140, 200),
    food=(255, 100, 100),  # Red food
    wall=(80, 90, 110),
    text=(200, 220, 255),
)

# Spring theme (March-May)
SPRING_THEME = Theme(
    name="spring",
    background=(20, 30, 20),
    grid_line=(40, 55, 40),
    contribution_0=(30, 40, 30),
    contribution_1=(80, 150, 80),
    contribution_2=(120, 180, 120),
    contribution_3=(150, 210, 150),
    contribution_4=(180, 255, 180),  # Light green
    snake_head=(255, 150, 200),  # Pink head
    snake_body=(255, 130, 180),
    snake_tail=(255, 110, 160),
    food=(255, 255, 100),  # Yellow food
    wall=(100, 80, 60),
    text=(200, 255, 200),
)

# Summer theme (June-August)
SUMMER_THEME = Theme(
    name="summer",
    background=(25, 25, 40),
    grid_line=(45, 45, 60),
    contribution_0=(35, 35, 50),
    contribution_1=(60, 100, 150),
    contribution_2=(80, 150, 200),
    contribution_3=(100, 200, 220),
    contribution_4=(150, 230, 255),  # Ocean blue
    snake_head=(255, 200, 50),  # Yellow/gold head
    snake_body=(255, 180, 30),
    snake_tail=(255, 160, 20),
    food=(255, 100, 100),  # Coral/red food
    wall=(100, 90, 80),
    text=(255, 240, 200),
)

# Space theme with galaxy vibes
SPACE_THEME = Theme(
    name="space",
    background=(8, 8, 24),  # Deep space blue-black
    grid_line=(20, 20, 40),  # Subtle grid
    contribution_0=(12, 12, 30),  # Empty space
    contribution_1=(40, 20, 80),  # Purple nebula (low)
    contribution_2=(80, 40, 140),  # Brighter purple
    contribution_3=(120, 60, 180),  # Vibrant purple
    contribution_4=(160, 100, 220),  # Bright magenta/purple
    snake_head=(0, 255, 200),  # Cyan/teal head
    snake_body=(0, 200, 160),  # Teal body
    snake_tail=(0, 150, 120),  # Darker teal tail
    food=(255, 220, 50),  # Golden star/food
    wall=(60, 40, 100),  # Dark purple walls
    text=(200, 200, 255),
)

THEMES: dict[ThemeName, Theme] = {
    "default": DEFAULT_THEME,
    "halloween": HALLOWEEN_THEME,
    "winter": WINTER_THEME,
    "spring": SPRING_THEME,
    "summer": SUMMER_THEME,
    "space": SPACE_THEME,
}


class ThemeManager:
    """Manages theme selection based on date or configuration."""

    def __init__(
        self,
        mode: Literal["auto", "force", "disable"] = "auto",
        forced_theme: str | None = None,
    ) -> None:
        """Initialize the theme manager.

        Args:
            mode: Theme selection mode.
            forced_theme: Theme to use when mode is "force".
        """
        self.mode = mode
        self.forced_theme = forced_theme

    def get_theme(self, current_date: date | None = None) -> Theme:
        """Get the appropriate theme.

        Args:
            current_date: Date to use for auto selection. Defaults to today.

        Returns:
            The selected theme.
        """
        if self.mode == "disable":
            return DEFAULT_THEME

        if self.mode == "force" and self.forced_theme:
            return THEMES.get(self.forced_theme, DEFAULT_THEME)

        # Auto mode: select based on date
        if current_date is None:
            current_date = date.today()

        return self._get_seasonal_theme(current_date)

    def _get_seasonal_theme(self, current_date: date) -> Theme:
        """Get theme based on the current date.

        Args:
            current_date: The date to check.

        Returns:
            The seasonal theme.
        """
        month = current_date.month
        day = current_date.day

        # Halloween: October 15-31
        if month == 10 and day >= 15:
            return HALLOWEEN_THEME

        # Winter: December, January, February
        if month in (12, 1, 2):
            return WINTER_THEME

        # Spring: March, April, May
        if month in (3, 4, 5):
            return SPRING_THEME

        # Summer: June, July, August
        if month in (6, 7, 8):
            return SUMMER_THEME

        # Default for September, early October, November
        return DEFAULT_THEME
