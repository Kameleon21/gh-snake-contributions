"""Data input modules for fetching and loading contribution data."""

from .github_fetcher import fetch_contributions
from .local_loader import load_local_contributions

__all__ = ["fetch_contributions", "load_local_contributions"]
