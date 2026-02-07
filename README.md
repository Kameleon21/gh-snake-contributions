# GitHub Snake Contributions

Transform your GitHub contributions into an animated Snake game!

![Snake Animation](https://raw.githubusercontent.com/Kameleon21/gh-snake-contributions/main/snake.gif)

## Add to Your Profile

1. Create `.github/workflows/snake.yml` in your profile repository (`USERNAME/USERNAME`):

```yaml
name: Generate Snake

on:
  schedule:
    - cron: "0 0 * * *" # Daily at midnight
  workflow_dispatch: # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: Kameleon21/gh-snake-contributions@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: Update snake animation
          file_pattern: snake.gif
```

2. Add to your `README.md`:

```markdown
![Snake](https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_USERNAME/main/snake.gif)
```

3. Manually trigger the workflow once, or wait for the daily run.

## Options

| Input              | Description                                                          | Default                |
| ------------------ | -------------------------------------------------------------------- | ---------------------- |
| `username`         | GitHub username                                                      | Repository owner       |
| `output`           | Output file path                                                     | `snake.gif`            |
| `theme`            | `auto`, `default`, `halloween`, `winter`, `spring`, `summer`, `space` | `default`              |
| `mode`             | `walls`, `food`, or `speed`                                          | `food`                 |
| `ai_strategy`      | `greedy`, `bfs_safe`, `survival`, `commit_hunter`                    | `commit_hunter`        |
| `spawn_position`   | `legacy_left`, `center`, `bottom_center`, `lower_half_random`        | `lower_half_random`    |
| `moves_per_second` | Snake movement updates per second                                    | `8.0`                  |
| `max_duration`     | Animation length (seconds)                                           | `12.0`                 |
| `fps`              | Frames per second                                                    | `12`                   |
| `seed`             | Random seed for reproducibility                                      | -                      |

## Inspired By

- [gh-space-shooter](https://github.com/czl9707/gh-space-shooter)

## License

MIT
