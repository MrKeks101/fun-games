# 006 — Tic-tac-toe interactive app: play one round

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-app`
**Depends on:** 002, 003, 004, 005

## Goal

Wire the pieces into a runnable window where two people can play a **single
round** of Tic-tac-toe hot-seat, see whose turn it is, and see the result when
it ends. Session score is recorded internally on round end (display + new round
come in ticket 007).

## Scope

Create:

- `games/tic_tac_toe/app.py` — the game loop: init `pygame`, create the window,
  poll events, translate clicks to moves via ticket 004, apply them via ticket
  002, redraw via ticket 005, cap the frame rate with a clock.
- `games/tic_tac_toe/__main__.py` — so `python -m games.tic_tac_toe` launches
  `app.py`.

Behaviour:

- Left-click on an empty cell places the current player's mark and passes the
  turn.
- Clicks on occupied cells or outside the board are ignored.
- When the round ends, the result banner shows and further board clicks are
  ignored.
- On round end, record the outcome into the score object from ticket 003
  **exactly once** (requirement 10) — guard against re-recording on subsequent
  frames.
- `Esc` or the window close button quits cleanly (`pygame.quit()`, no
  traceback).

## Separation / coverage guidance

Keep `app.py` thin: a testable step function (e.g. `handle_event(state, event)`
returning new state, and `advance`/`apply_click(state, point)`) with the raw
`while` loop delegating to it. Unit-test the step function by feeding it
synthetic events / points headlessly. The bare `while` loop and
`pygame.display.flip()` may carry `# pragma: no cover` if unavoidable, but keep
that surface as small as possible — the click→move→outcome→score path must be
covered by tests.

## Out of scope

- On-screen scoreboard and the new-round control (ticket 007). It is fine if
  the score is tracked but not yet visible, and if the only way to start over
  is to relaunch.

## Acceptance criteria

- [ ] `python -m games.tic_tac_toe` opens a window showing an empty board and
      the turn indicator.
- [ ] Clicking empty cells alternately places `X` then `O`.
- [ ] Clicking an occupied cell or outside the board does nothing.
- [ ] Completing a line shows the correct win banner and highlights the line;
      the board stops accepting moves.
- [ ] Filling the board with no line shows the draw banner.
- [ ] The round outcome is recorded into the score object exactly once.
- [ ] `Esc` and the window close button both exit without a traceback.
- [ ] Headless tests cover the click→move→win/draw→score-record path.
- [ ] `pytest --cov=games --cov-fail-under=90` passes.

## Expected tests

`tests/tic_tac_toe/test_app.py` (headless) — synthetic click sequence produces
an `X` win and records exactly one `X` win; a drawing sequence records exactly
one draw; clicks after game over are no-ops and do not double-record; a click
on an occupied cell is a no-op; quit event ends the loop.
