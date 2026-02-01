"""GitHub API integration for fetching contribution data."""

import os
from typing import Any

import httpx

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

CONTRIBUTION_QUERY = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
          }
        }
      }
    }
  }
}
"""

# GitHub contribution levels map to 0-4
CONTRIBUTION_LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def fetch_contributions(
    username: str,
    token: str | None = None,
) -> list[list[int]]:
    """Fetch contribution data from GitHub GraphQL API.

    Args:
        username: GitHub username to fetch contributions for.
        token: GitHub API token. Uses GITHUB_TOKEN env var if not provided.

    Returns:
        2D list of contribution levels (7 rows × 52+ columns).
        Each value is 0-4 representing contribution intensity.

    Raises:
        ValueError: If no token is provided and GITHUB_TOKEN is not set.
        httpx.HTTPError: If the API request fails.
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise ValueError(
            "GitHub token required. Set GITHUB_TOKEN environment variable "
            "or pass token parameter."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": CONTRIBUTION_QUERY,
        "variables": {"username": username},
    }

    with httpx.Client() as client:
        response = client.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

    return _parse_contribution_data(data)


def _parse_contribution_data(data: dict[str, Any]) -> list[list[int]]:
    """Parse the GraphQL response into a 2D contribution grid.

    Args:
        data: Raw GraphQL response.

    Returns:
        2D list with 7 rows (days) × N columns (weeks).
    """
    try:
        weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (KeyError, TypeError) as e:
        raise ValueError(f"Invalid GitHub API response: {e}") from e

    # GitHub returns weeks as columns, days as rows (0=Sunday, 6=Saturday)
    # Convert to 7 rows × N columns
    grid: list[list[int]] = [[] for _ in range(7)]

    for week in weeks:
        days = week["contributionDays"]
        for i, day in enumerate(days):
            level_str = day.get("contributionLevel", "NONE")
            level = CONTRIBUTION_LEVEL_MAP.get(level_str, 0)
            grid[i].append(level)

    return grid


async def fetch_contributions_async(
    username: str,
    token: str | None = None,
) -> list[list[int]]:
    """Async version of fetch_contributions.

    Args:
        username: GitHub username to fetch contributions for.
        token: GitHub API token. Uses GITHUB_TOKEN env var if not provided.

    Returns:
        2D list of contribution levels (7 rows × 52+ columns).

    Raises:
        ValueError: If no token is provided and GITHUB_TOKEN is not set.
        httpx.HTTPError: If the API request fails.
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise ValueError(
            "GitHub token required. Set GITHUB_TOKEN environment variable "
            "or pass token parameter."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": CONTRIBUTION_QUERY,
        "variables": {"username": username},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

    return _parse_contribution_data(data)
