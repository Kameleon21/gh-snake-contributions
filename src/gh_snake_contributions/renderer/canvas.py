"""Frame rendering using Pillow."""

import random
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

from ..game.board import CellType, Position
from ..game.engine import GameState
from .themes import Theme

if TYPE_CHECKING:
    from ..config import Config


class Canvas:
    """Renders game frames using Pillow."""

    def __init__(self, config: "Config", theme: Theme) -> None:
        """Initialize the canvas.

        Args:
            config: Game configuration.
            theme: Color theme to use.
        """
        self.config = config
        self.theme = theme
        self.cell_size = config.cell_size
        self.width = config.width * config.cell_size
        self.height = config.height * config.cell_size

        # Pre-generate star positions for space theme (seeded for consistency)
        self._stars: list[tuple[int, int, int]] = []
        if theme.name == "space":
            rng = random.Random(42)  # Fixed seed for consistent stars
            for _ in range(50):  # 50 stars
                x = rng.randint(0, self.width - 1)
                y = rng.randint(0, self.height - 1)
                brightness = rng.randint(150, 255)
                self._stars.append((x, y, brightness))

    def render_frame(self, state: GameState) -> Image.Image:
        """Render a single frame of the game.

        Args:
            state: Current game state.

        Returns:
            PIL Image of the frame.
        """
        # Create image with background color
        image = Image.new("RGB", (self.width, self.height), self.theme.background)
        draw = ImageDraw.Draw(image)

        # Render stars for space theme
        if self._stars:
            self._render_stars(draw)

        # Render layers in order
        self._render_contribution_cells(draw, state)
        self._render_grid(draw)
        self._render_walls(draw, state)
        self._render_food(draw, state)
        self._render_snake(draw, state)

        return image

    def _cell_rect(self, pos: Position) -> tuple[int, int, int, int]:
        """Get the rectangle coordinates for a cell.

        Args:
            pos: Cell position.

        Returns:
            (x1, y1, x2, y2) coordinates.
        """
        x1 = pos.x * self.cell_size
        y1 = pos.y * self.cell_size
        x2 = x1 + self.cell_size - 1
        y2 = y1 + self.cell_size - 1
        return (x1, y1, x2, y2)

    def _render_contribution_cells(self, draw: ImageDraw.ImageDraw, state: GameState) -> None:
        """Render contribution level cells as background.

        Args:
            draw: ImageDraw object.
            state: Game state.
        """
        board = state.board
        for y in range(board.height):
            for x in range(board.width):
                cell = board.cells[y][x]
                if cell.cell_type == CellType.WALL:
                    continue  # Walls rendered separately

                level = cell.contribution_level
                if level > 0:
                    color = self.theme.get_contribution_color(level)
                    rect = self._cell_rect(Position(x, y))
                    # Inset the cell slightly for visual separation
                    inset = 1
                    inner_rect = (
                        rect[0] + inset,
                        rect[1] + inset,
                        rect[2] - inset,
                        rect[3] - inset,
                    )
                    draw.rectangle(inner_rect, fill=color)

    def _render_stars(self, draw: ImageDraw.ImageDraw) -> None:
        """Render stars for space theme.

        Args:
            draw: ImageDraw object.
        """
        for x, y, brightness in self._stars:
            color = (brightness, brightness, brightness)
            draw.point((x, y), fill=color)
            # Some stars are slightly larger
            if brightness > 220:
                draw.point((x + 1, y), fill=(brightness - 50, brightness - 50, brightness - 50))
                draw.point((x, y + 1), fill=(brightness - 50, brightness - 50, brightness - 50))

    def _render_grid(self, draw: ImageDraw.ImageDraw) -> None:
        """Render grid lines.

        Args:
            draw: ImageDraw object.
        """
        color = self.theme.grid_line

        # Vertical lines
        for x in range(0, self.width + 1, self.cell_size):
            draw.line([(x, 0), (x, self.height)], fill=color, width=1)

        # Horizontal lines
        for y in range(0, self.height + 1, self.cell_size):
            draw.line([(0, y), (self.width, y)], fill=color, width=1)

    def _render_walls(self, draw: ImageDraw.ImageDraw, state: GameState) -> None:
        """Render wall cells.

        Args:
            draw: ImageDraw object.
            state: Game state.
        """
        board = state.board
        for y in range(board.height):
            for x in range(board.width):
                cell = board.cells[y][x]
                if cell.cell_type == CellType.WALL:
                    rect = self._cell_rect(Position(x, y))
                    # Fill the entire cell for walls
                    draw.rectangle(rect, fill=self.theme.wall)

    def _render_food(self, draw: ImageDraw.ImageDraw, state: GameState) -> None:
        """Render the food item.

        Args:
            draw: ImageDraw object.
            state: Game state.
        """
        if state.food is None:
            return

        rect = self._cell_rect(state.food)
        # Draw food as a filled circle
        inset = 2
        circle_rect = (
            rect[0] + inset,
            rect[1] + inset,
            rect[2] - inset,
            rect[3] - inset,
        )
        draw.ellipse(circle_rect, fill=self.theme.food)

    def _render_snake(self, draw: ImageDraw.ImageDraw, state: GameState) -> None:
        """Render the snake.

        Args:
            draw: ImageDraw object.
            state: Game state.
        """
        snake = state.snake
        body_list = list(snake.body)

        for i, pos in enumerate(body_list):
            rect = self._cell_rect(pos)
            inset = 1

            if i == 0:
                # Head
                color = self.theme.snake_head
                inset = 1
            elif i == len(body_list) - 1:
                # Tail
                color = self.theme.snake_tail
                inset = 2
            else:
                # Body
                color = self.theme.snake_body
                inset = 1

            inner_rect = (
                rect[0] + inset,
                rect[1] + inset,
                rect[2] - inset,
                rect[3] - inset,
            )

            if i == 0:
                # Draw head as rounded rectangle (approximated with ellipse corners)
                draw.rounded_rectangle(inner_rect, radius=3, fill=color)
                # Add eyes
                self._draw_eyes(draw, pos, snake.direction)
            else:
                draw.rectangle(inner_rect, fill=color)

    def _draw_eyes(
        self,
        draw: ImageDraw.ImageDraw,
        head_pos: Position,
        direction: "Direction",
    ) -> None:
        """Draw eyes on the snake head.

        Args:
            draw: ImageDraw object.
            head_pos: Position of the head.
            direction: Direction the snake is facing.
        """
        from ..game.snake import Direction

        cx = head_pos.x * self.cell_size + self.cell_size // 2
        cy = head_pos.y * self.cell_size + self.cell_size // 2

        eye_size = max(2, self.cell_size // 6)
        eye_offset = self.cell_size // 4

        # Position eyes based on direction
        if direction == Direction.UP:
            eye1 = (cx - eye_offset, cy - eye_offset // 2)
            eye2 = (cx + eye_offset, cy - eye_offset // 2)
        elif direction == Direction.DOWN:
            eye1 = (cx - eye_offset, cy + eye_offset // 2)
            eye2 = (cx + eye_offset, cy + eye_offset // 2)
        elif direction == Direction.LEFT:
            eye1 = (cx - eye_offset // 2, cy - eye_offset)
            eye2 = (cx - eye_offset // 2, cy + eye_offset)
        else:  # RIGHT
            eye1 = (cx + eye_offset // 2, cy - eye_offset)
            eye2 = (cx + eye_offset // 2, cy + eye_offset)

        # Draw white of eyes
        for eye in (eye1, eye2):
            eye_rect = (
                eye[0] - eye_size,
                eye[1] - eye_size,
                eye[0] + eye_size,
                eye[1] + eye_size,
            )
            draw.ellipse(eye_rect, fill=(255, 255, 255))

        # Draw pupils (smaller, black)
        pupil_size = max(1, eye_size // 2)
        for eye in (eye1, eye2):
            pupil_rect = (
                eye[0] - pupil_size,
                eye[1] - pupil_size,
                eye[0] + pupil_size,
                eye[1] + pupil_size,
            )
            draw.ellipse(pupil_rect, fill=(0, 0, 0))
