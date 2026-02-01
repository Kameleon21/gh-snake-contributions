"""CLI entry point for GitHub Snake Contributions."""

import argparse
import sys
from pathlib import Path

from .ai import AIController
from .config import Config
from .data import fetch_contributions, load_local_contributions
from .encoder import GifEncoder
from .game import GameEngine
from .renderer import Canvas, ThemeManager


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="gh-snake-contributions",
        description="Transform your GitHub contributions into an animated Snake game GIF",
    )

    # Data source (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--username",
        "-u",
        help="GitHub username to fetch contributions for",
    )
    source_group.add_argument(
        "--local",
        "-l",
        type=Path,
        help="Path to local JSON file with contribution data",
    )

    # Board settings
    parser.add_argument(
        "--width",
        "-W",
        type=int,
        default=30,
        help="Board width in cells (default: 30)",
    )
    parser.add_argument(
        "--height",
        "-H",
        type=int,
        default=15,
        help="Board height in cells (default: 15)",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=16,
        help="Cell size in pixels (default: 16)",
    )

    # Game settings
    parser.add_argument(
        "--mode",
        "-m",
        choices=["walls", "food", "speed"],
        default="walls",
        help="How contributions affect gameplay (default: walls)",
    )
    parser.add_argument(
        "--wall-threshold",
        type=int,
        default=3,
        help="Contribution level threshold for walls (default: 3)",
    )
    parser.add_argument(
        "--ai-strategy",
        choices=["greedy", "bfs_safe", "survival"],
        default="bfs_safe",
        help="AI strategy for snake movement (default: bfs_safe)",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=500,
        help="Maximum game ticks before timeout (default: 500)",
    )

    # GIF settings
    parser.add_argument(
        "--output",
        "-o",
        default="snake.gif",
        help="Output GIF file path (default: snake.gif)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=12,
        help="Frames per second (default: 12)",
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=8.0,
        help="Maximum animation duration in seconds (default: 8.0)",
    )

    # Theme settings
    parser.add_argument(
        "--theme",
        "-t",
        choices=["auto", "default", "halloween", "winter", "spring", "summer"],
        default="auto",
        help="Color theme (default: auto based on date)",
    )

    # Determinism
    parser.add_argument(
        "--seed",
        "-s",
        help="Random seed for deterministic output",
    )

    # Verbosity
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output messages",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Determine theme mode
    if args.theme == "auto":
        theme_mode = "auto"
        forced_theme = None
    else:
        theme_mode = "force"
        forced_theme = args.theme

    # Parse seed
    seed = None
    if args.seed:
        try:
            seed = int(args.seed)
        except ValueError:
            seed = args.seed  # Use as string

    # Create configuration
    config = Config(
        width=args.width,
        height=args.height,
        cell_size=args.cell_size,
        contribution_mode=args.mode,
        wall_threshold=args.wall_threshold,
        ai_strategy=args.ai_strategy,
        max_ticks=args.max_ticks,
        fps=args.fps,
        max_duration=args.max_duration,
        output_path=args.output,
        theme_mode=theme_mode,
        forced_theme=forced_theme,
        seed=seed,
    )

    # Load contribution data
    contributions: list[list[int]] | None = None

    if args.local:
        if not args.quiet:
            print(f"Loading contributions from {args.local}...")
        try:
            contributions = load_local_contributions(args.local)
        except Exception as e:
            print(f"Error loading local file: {e}", file=sys.stderr)
            return 1
    elif args.username:
        if not args.quiet:
            print(f"Fetching contributions for {args.username}...")
        try:
            contributions = fetch_contributions(args.username)
        except Exception as e:
            print(f"Error fetching contributions: {e}", file=sys.stderr)
            return 1

    # Set up theme
    theme_manager = ThemeManager(mode=config.theme_mode, forced_theme=config.forced_theme)
    theme = theme_manager.get_theme()

    if not args.quiet:
        print(f"Using theme: {theme.name}")

    # Initialize game components
    engine = GameEngine(config)
    engine.setup(contributions)

    ai = AIController(config)
    canvas = Canvas(config, theme)
    encoder = GifEncoder(config)

    # Run game simulation
    if not args.quiet:
        print("Running game simulation...")

    max_frames = config.max_frames
    frame_count = 0

    while engine.is_running() and frame_count < max_frames:
        # Get current state and render frame
        state = engine.get_state()
        frame = canvas.render_frame(state)
        encoder.add_frame(frame)

        # Get AI decision and step
        direction = ai.get_next_direction(state)
        engine.step(direction)

        frame_count += 1

    # Render final frame
    state = engine.get_state()
    frame = canvas.render_frame(state)
    encoder.add_frame(frame)

    # Save GIF
    if not args.quiet:
        print(f"Game ended: {state.status} (score: {state.score}, ticks: {state.tick})")
        print(f"Saving GIF to {config.output_path}...")

    try:
        output_path = encoder.save()
        if not args.quiet:
            print(f"Done! Saved {encoder.frame_count} frames to {output_path}")
    except Exception as e:
        print(f"Error saving GIF: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
