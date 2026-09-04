"""Tic-tac-toe — a local, offline 3x3 game for the ``fun-games`` collection.

This first iteration is two-player hot-seat only: two humans share one machine
and take turns, with ``X`` always moving first. The app detects wins and draws,
shows the result, and keeps a running score across rounds within a session.

See ``docs/requirements/tic-tac-toe.md`` for the full requirements. Game-rule and
score logic are kept in plain Python modules with no ``pygame`` import so they
are unit-testable without a display.
"""
