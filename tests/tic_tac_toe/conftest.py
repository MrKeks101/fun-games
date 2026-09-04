"""Headless pygame setup for the tic-tac-toe render tests.

Force SDL onto its dummy video/audio drivers *before* pygame is imported so the
render smoke tests never need a real display or sound card.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402 - must follow the env setup above
import pytest  # noqa: E402

from games.tic_tac_toe.layout import DEFAULT_LAYOUT  # noqa: E402


@pytest.fixture
def surface() -> pygame.Surface:
    """A fresh off-screen surface the size of the game window, filled black."""
    surf = pygame.Surface(DEFAULT_LAYOUT.window_size)
    surf.fill((0, 0, 0))
    return surf
