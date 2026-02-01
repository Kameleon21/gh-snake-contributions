# GitHub Snake Contributions

Transform your GitHub contributions into an animated Snake game GIF!

![Snake Animation](https://raw.githubusercontent.com/Kameleon21/gh-snake-contributions/main/snake.gif)

## Features

- Fetches your GitHub contribution data and turns it into a Snake game
- Contribution intensity becomes walls (or food/speed modifiers)
- Smart AI plays the game to generate entertaining animations
- Seasonal themes that automatically change based on the date
- Deterministic output with seed support
- GitHub Action for automatic daily updates

## Quick Start

### Using GitHub Actions (Recommended)

1. Fork this repository
2. Enable GitHub Actions in your fork
3. The workflow will automatically generate a new snake animation daily
4. Add to your profile README:

```markdown
![Snake Animation](https://raw.githubusercontent.com/YOUR_USERNAME/gh-snake-contributions/main/snake.gif)
```

### Manual Generation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gh-snake-contributions
cd gh-snake-contributions

# Install dependencies with uv
uv sync

# Generate with your GitHub username
export GITHUB_TOKEN=your_token_here
uv run gh-snake-contributions --username YOUR_USERNAME

# Or use local test data
uv run gh-snake-contributions --local tests/fixtures/sample_contributions.json
```

## Usage

```
gh-snake-contributions [OPTIONS]

Options:
  --username, -u TEXT     GitHub username to fetch contributions for
  --local, -l PATH        Path to local JSON file with contribution data
  --width, -W INT         Board width in cells (default: 30)
  --height, -H INT        Board height in cells (default: 15)
  --cell-size INT         Cell size in pixels (default: 16)
  --mode, -m TEXT         How contributions affect gameplay: walls|food|speed (default: walls)
  --wall-threshold INT    Contribution level threshold for walls (default: 3)
  --ai-strategy TEXT      AI strategy: greedy|bfs_safe|survival (default: bfs_safe)
  --max-ticks INT         Maximum game ticks before timeout (default: 500)
  --output, -o TEXT       Output GIF file path (default: snake.gif)
  --fps INT               Frames per second (default: 12)
  --max-duration FLOAT    Maximum animation duration in seconds (default: 8.0)
  --theme, -t TEXT        Color theme: auto|default|halloween|winter|spring|summer
  --seed, -s TEXT         Random seed for deterministic output
  --quiet, -q             Suppress output messages
```

## Contribution Modes

- **walls** (default): High contribution cells become walls the snake must avoid
- **food**: Contribution cells spawn food items
- **speed**: Contribution levels affect snake speed

## Themes

The tool includes seasonal themes that automatically activate based on the current date:

| Theme | Season |
|-------|--------|
| Default | September, early October, November |
| Halloween | October 15-31 |
| Winter | December - February |
| Spring | March - May |
| Summer | June - August |

Override with `--theme <name>` to use a specific theme.

## Using as a GitHub Action

Add to your workflow:

```yaml
- uses: YOUR_USERNAME/gh-snake-contributions@main
  with:
    username: ${{ github.repository_owner }}
    output: 'snake.gif'
    theme: 'auto'
```

### Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `username` | GitHub username | Repository owner |
| `output` | Output file path | `snake.gif` |
| `theme` | Color theme | `auto` |
| `mode` | Contribution mode | `walls` |
| `width` | Board width | `30` |
| `height` | Board height | `15` |
| `fps` | Frames per second | `12` |
| `max_duration` | Max duration (seconds) | `8.0` |
| `seed` | Random seed | (none) |

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=gh_snake_contributions
```

## Local Contribution Data Format

For testing without GitHub API access:

```json
{
  "contributions": [
    [0, 1, 2, 3, 4, 0, 1, ...],
    [1, 0, 2, 1, 3, 2, 0, ...],
    ...
  ]
}
```

Each row represents a day of the week (0=Sunday through 6=Saturday), and each column represents a week. Values are 0-4 representing contribution intensity.

## Inspired By

- [gh-space-shooter](https://github.com/czl9707/gh-space-shooter) - Transform GitHub contributions into a space shooter game

## License

MIT
