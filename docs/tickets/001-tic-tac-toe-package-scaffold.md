# 001 — Tic-tac-toe package scaffold

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-scaffold`
**Depends on:** none

## Goal

Create the package skeleton for the Tic-tac-toe game and its test package so
later tickets have a place to land. No game logic and no interactive window
yet — just structure that keeps `main` green.

## Scope

- Create `games/__init__.py` (if missing) and `games/tic_tac_toe/__init__.py`.
- Add a module docstring to `games/tic_tac_toe/__init__.py` briefly describing
  the game and pointing at the requirements doc.
- Create `tests/__init__.py` (if needed) and `tests/tic_tac_toe/` with an
  `__init__.py`.
- Add one trivial test that imports `games.tic_tac_toe` and asserts the package
  imports cleanly (this exists mainly to keep the test session non-empty and
  wire up coverage on the new package).
- Add `games/tic_tac_toe/README.md` stub: one line on what it is, and a
  "How to run" section marked _TBD (see ticket 007)_.

## Out of scope

- Board/rules logic (ticket 002).
- Any `pygame` import or window (ticket 006).

## Acceptance criteria

- [ ] `games/tic_tac_toe/` is an importable package with a docstring.
- [ ] `tests/tic_tac_toe/` exists and mirrors the game package.
- [ ] `pytest` from the repo root collects and passes at least one test.
- [ ] `pytest --cov=games --cov-fail-under=90` passes (coverage is trivially
      100% since there is no executable logic yet).
- [ ] `games/tic_tac_toe/README.md` exists.
- [ ] No `pygame` import anywhere in this ticket's changes.

## Expected tests

- `tests/tic_tac_toe/test_package.py` — imports the package and asserts it is a
  module.
