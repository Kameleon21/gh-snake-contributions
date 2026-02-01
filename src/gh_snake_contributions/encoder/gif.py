"""GIF encoding for animation output."""

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from ..config import Config


class GifEncoder:
    """Encodes frames into an animated GIF."""

    def __init__(self, config: "Config") -> None:
        """Initialize the GIF encoder.

        Args:
            config: Game configuration.
        """
        self.config = config
        self.frames: list[Image.Image] = []

    def add_frame(self, frame: Image.Image) -> None:
        """Add a frame to the animation.

        Args:
            frame: PIL Image to add.
        """
        # Convert to P mode (palette) for better GIF compression
        # but keep as RGB for now, convert during save
        self.frames.append(frame.copy())

    def save(self, output_path: str | Path | None = None) -> Path:
        """Save the animation as a GIF.

        Args:
            output_path: Path to save the GIF. Uses config default if None.

        Returns:
            Path to the saved GIF.
        """
        if output_path is None:
            output_path = self.config.output_path

        output_path = Path(output_path)

        if not self.frames:
            raise ValueError("No frames to save")

        # Calculate frame duration
        duration = self.config.frame_duration_ms

        # Convert frames to palette mode for better GIF quality
        optimized_frames = []
        for frame in self.frames:
            # Quantize to 256 colors for GIF
            optimized = frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
            optimized_frames.append(optimized)

        # Save as animated GIF
        optimized_frames[0].save(
            output_path,
            save_all=True,
            append_images=optimized_frames[1:],
            duration=duration,
            loop=0,  # Loop forever
            optimize=False,  # Already optimized
        )

        return output_path

    def clear(self) -> None:
        """Clear all frames."""
        self.frames.clear()

    @property
    def frame_count(self) -> int:
        """Get the number of frames."""
        return len(self.frames)
