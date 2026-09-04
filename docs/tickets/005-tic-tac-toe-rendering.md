# 005 — Tic-tac-toe rendering

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-rendering`
**Depends on:** 002, 004

## Goal

Draw the game onto a `pygame.Surface`. This ticket introduces `pygame` but
**not** the event loop — every function takes a surface plus plain state and
draws; no `pygame.display`, no clock, no input.

## Scope

Create `games/tic_tac_toe/render.py` providing functions that, given a target
surface and the current state, draw:

- the 3x3 grid using the layout from ticket 004;
- `X` and `O` marks in their cells;
- a turn indicator ("X to move" / "O to move") while the round is in progress;
- the scoreboard: `X` wins, `O` wins, draws (values passed in as ints);
- a result banner when the round is over ("X wins!" / "O wins!" / "Draw"),
  and a highlight over the winning line when there is one;
- the "new round" button.

A single top-level `draw(surface, view_state)` entry point that composes the
above is fine and encouraged.

## Testing approach

Run headless: set `SDL_VIDEODRIVER=dummy` (and `SDL_AUDIODRIVER=dummy`) in a
fixture, create an off-screen `pygame.Surface`, call the draw functions, and
assert they run without error and change pixels where expected (e.g. sample a
pixel in a drawn cell, or assert the surface is not uniformly the background
color). Keep assertions coarse — this is a smoke test, not pixel-perfect
snapshotting.

## Out of scope

- Opening a window, event handling, the game loop (ticket 006).
- Deciding game state transitions (tickets 002/003).

## Acceptance criteria

- [ ] `render.py` does not import `pygame.display` / open a window; it only
      draws onto a surface passed to it.
- [ ] Each draw function runs headlessly without raising for: empty board,
      mid-game board, `X`-win board (with winning line), `O`-win board, draw
      board.
- [ ] The turn indicator reflects the passed-in current player and is absent /
      replaced by the result banner once the round is over.
- [ ] The scoreboard shows the three integer values it is given.
- [ ] Winning-line highlight is drawn only when a winning line is provided.
- [ ] `pytest --cov=games --cov-fail-under=90` passes (headless render tests
      keep this module covered).

## Expected tests

`tests/tic_tac_toe/test_render.py` — headless fixture; smoke-render each board
state; assert surface changed; assert turn indicator vs result banner switch
based on state; winning-line highlight only when supplied.
