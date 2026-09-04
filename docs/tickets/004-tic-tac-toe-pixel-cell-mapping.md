# 004 — Tic-tac-toe pixel/cell mapping (pure logic)

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-hit-testing`
**Depends on:** 002

## Goal

Pure geometry helpers that translate between screen pixels and board cells, and
hit-test the "new round" control. **No `pygame` import** (operate on plain
numbers / simple layout data — a `pygame.Rect` is not required, a tuple works).

## Scope

Create `games/tic_tac_toe/layout.py` (name is the developer's call) providing:

- a layout description for the board given the window size / board origin /
  board pixel size / cell size (a small dataclass or a function returning
  cell rectangles as plain tuples);
- `cell_at(point)` — given an `(x, y)` pixel, return the cell index `0..8`, or
  `None` if the point is outside the board (including on grid-line gutters if
  the design has them);
- a rect (as a plain tuple) for the "new round" button and a
  `point_in_new_round_button(point)` helper.

Keep numbers configurable (constants module or function args) so ticket 005/006
can share them.

## Out of scope

- Actually drawing anything (ticket 005).
- Handling events (ticket 006).

## Acceptance criteria

- [ ] Module has no `import pygame`.
- [ ] Clicking the center of each of the 9 cells returns that cell's index.
- [ ] Clicking clearly outside the board returns `None`.
- [ ] Corner/boundary points map to a sensible, documented cell (or `None`) —
      behaviour is defined, not accidental.
- [ ] `point_in_new_round_button` is `True` inside the button rect and `False`
      outside.
- [ ] `pytest --cov=games --cov-fail-under=90` passes.

## Expected tests

`tests/tic_tac_toe/test_layout.py` — center of every cell → correct index;
points outside → `None`; a couple of boundary cases; new-round button hit-test
inside and outside.
