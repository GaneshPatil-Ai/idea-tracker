"""Compatibility wrapper forwarding to modular src layout."""

from idea_tracker.main import app, cli_main

if __name__ == "__main__":
    cli_main()

__all__ = ["app"]
