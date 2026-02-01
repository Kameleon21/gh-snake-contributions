"""Local JSON loader for testing and development."""

import json
from pathlib import Path


def load_local_contributions(file_path: str | Path) -> list[list[int]]:
    """Load contribution data from a local JSON file.

    The JSON file should contain a 2D array of integers (0-4)
    representing contribution levels.

    Example format:
    {
        "contributions": [
            [0, 1, 2, 3, 4, 0, 1, ...],  // Day 0 (Sunday) for each week
            [1, 0, 2, 1, 3, 2, 0, ...],  // Day 1 (Monday) for each week
            ...
        ]
    }

    Or simply a 2D array:
    [
        [0, 1, 2, 3, 4, 0, 1, ...],
        [1, 0, 2, 1, 3, 2, 0, ...],
        ...
    ]

    Args:
        file_path: Path to the JSON file.

    Returns:
        2D list of contribution levels.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file isn't valid JSON.
        ValueError: If the data format is invalid.
    """
    file_path = Path(file_path)

    with open(file_path) as f:
        data = json.load(f)

    # Handle both formats
    if isinstance(data, dict):
        if "contributions" in data:
            contributions = data["contributions"]
        else:
            raise ValueError("JSON object must contain 'contributions' key")
    elif isinstance(data, list):
        contributions = data
    else:
        raise ValueError("JSON must be a 2D array or object with 'contributions' key")

    # Validate structure
    if not contributions or not isinstance(contributions, list):
        raise ValueError("Contributions must be a non-empty list")

    if not all(isinstance(row, list) for row in contributions):
        raise ValueError("Contributions must be a 2D list")

    # Validate values are in range 0-4
    for row in contributions:
        for val in row:
            if not isinstance(val, int) or val < 0 or val > 4:
                raise ValueError(f"Contribution values must be integers 0-4, got {val}")

    return contributions


def generate_sample_contributions(
    weeks: int = 52,
    seed: int | None = None,
) -> list[list[int]]:
    """Generate sample contribution data for testing.

    Args:
        weeks: Number of weeks of data to generate.
        seed: Random seed for reproducibility.

    Returns:
        2D list of contribution levels (7 rows × weeks columns).
    """
    import random

    if seed is not None:
        random.seed(seed)

    # Generate 7 days × N weeks
    contributions: list[list[int]] = []

    for _ in range(7):  # 7 days
        row: list[int] = []
        for _ in range(weeks):
            # Weighted towards lower contribution levels
            weights = [0.4, 0.25, 0.2, 0.1, 0.05]
            val = random.choices(range(5), weights=weights)[0]
            row.append(val)
        contributions.append(row)

    return contributions


def save_sample_contributions(
    file_path: str | Path,
    weeks: int = 52,
    seed: int | None = None,
) -> None:
    """Generate and save sample contribution data.

    Args:
        file_path: Path to save the JSON file.
        weeks: Number of weeks of data to generate.
        seed: Random seed for reproducibility.
    """
    contributions = generate_sample_contributions(weeks, seed)

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump({"contributions": contributions}, f, indent=2)
