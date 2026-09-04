# 007 — Tic-tac-toe multi-round play + on-screen scoreboard

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-multi-round`
**Depends on:** 006

## Goal

Turn the single-round app into a session: show the running score on screen at
all times, and let players start a new round without losing the score.

## Scope

- Draw the scoreboard every frame (uses the render function from ticket 005),
  wired to the live score object from ticket 003.
- Add the "new round" control:
  - clickable on-screen button (hit-tested via ticket 004);
  - key shortcut `N` (see open question 3 in the requirements — `Space` too if
    trivial).
- Starting a new round: clear the board and result, keep the score, `X` moves
  first again (requirement 9).
- The new-round control is available both mid-round (abandon and restart —
  abandoning does **not** touch the score) and after a round ends.
- Update `games/tic_tac_toe/README.md`: fill in the "How to run" section
  (`python -m games.tic_tac_toe`), controls (click to place, `N` new round,
  `Esc` quit), and a one-line note that score is session-only.

## Out of scope

- A "reset score" control (the score object supports it from ticket 003, but
  exposing it in the UI is not required here — leave a note if you skip it).
- First-player alternation / loser-starts (open question 1; default stays
  `X`-always).

## Acceptance criteria

- [ ] The scoreboard (`X` wins / `O` wins / draws) is visible at all times and
      updates immediately when a round ends.
- [ ] Playing several rounds accumulates the score correctly; each finished
      round changes exactly one counter by exactly one.
- [ ] The "new round" button and the `N` key both start a fresh round with an
      empty board, no result banner, and `X` to move.
- [ ] Starting a new round keeps the accumulated score.
- [ ] Using "new round" mid-round (before it ends) does not change the score.
- [ ] Closing and relaunching the app resets the score to 0 / 0 / 0 (confirms
      no persistence — this is intended).
- [ ] `Esc` / window close still quit cleanly.
- [ ] `README.md` "How to run" and controls are filled in.
- [ ] `pytest --cov=games --cov-fail-under=90` passes.

## Expected tests

`tests/tic_tac_toe/test_app.py` (extend) — headless: two full rounds with
different outcomes leave the score at the expected 3 values; `N` key and
new-round-button events both reset the board while preserving score; new round
mid-play does not record anything; `X` is to move after a reset.
