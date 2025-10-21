import os
import sys
from pathlib import Path

# Add current directory to Python path for relative imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add parent directory to Python path for project modules (db, parser, etc.)
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Suppress ALSA audio errors that don't affect functionality
os.environ['ALSA_PCM_CARD'] = 'default'
os.environ['ALSA_PCM_DEVICE'] = '0'

import flet as ft

from core.app import App


def main(page: ft.Page) -> None:
    """Entry point for the Flet application."""
    App(page).run()


if __name__ == "__main__":
    ft.app(main)
