# 002 — Tic-tac-toe rules engine (pure logic)

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-rules-engine`
**Depends on:** 001

## Goal

Implement the core game-rule logic for a single round of Tic-tac-toe as plain
Python with **no `pygame` import**. This is the testable heart of the game.

## Scope

Create `games/tic_tac_toe/game.py` (name is the developer's call) providing:

- A representation of the two marks (`X`, `O`) — e.g. an `Enum`.
- A board of 9 cells, indexed `0..8` (row-major: index `= row * 3 + col`).
- A round/game object or set of functions exposing:
  - the current board contents;
  - whose turn it is (starts at `X`);
  - the set/list of legal moves (indices of empty cells) — empty when the
    round is over;
  - a way to apply a move by cell index;
  - the round status: in progress, `X` wins, `O` wins, or draw;
  - the winning line (the 3 cell indices) when there is a winner, else `None`.
- A `new_round` / reset affordance that returns the round to the start state
  with `X` to move.

## Rules to enforce

- Marks alternate starting with `X`; exactly one cell filled per move.
- Applying a move to a non-empty cell is rejected (raise a clear exception or
  return a documented "rejected" result — pick one and be consistent). A
  rejected move does not change whose turn it is.
- Applying a move once the round is already won or drawn is rejected the same
  way.
- After a move: check for a completed line (win for the mover) **before**
  checking for a full board (draw).
- All 8 lines detected: rows `{0,1,2},{3,4,5},{6,7,8}`, columns
  `{0,3,6},{1,4,7},{2,5,8}`, diagonals `{0,4,8},{2,4,6}`.

## Out of scope

- Scorekeeping across rounds (ticket 003).
- Any rendering, input, or main loop.

## Acceptance criteria

- [ ] Module has no `import pygame`.
- [ ] Fresh round: board empty, `X` to move, status is "in progress", 9 legal
      moves.
- [ ] A legal move fills the chosen cell and flips the turn.
- [ ] Illegal move (occupied cell) is rejected and leaves board + turn
      unchanged.
- [ ] Win is detected for every one of the 8 lines, for both `X` and `O`, and
      the winning line indices are reported.
- [ ] A board that fills with no line reports "draw".
- [ ] A move that both completes a line and fills the last empty cell is
      reported as a win, not a draw.
- [ ] After the round is over, legal moves is empty and further moves are
      rejected.
- [ ] `new_round`/reset returns to the start state.
- [ ] `pytest --cov=games --cov-fail-under=90` passes.

## Expected tests

`tests/tic_tac_toe/test_game.py`, covering: initial state; turn alternation;
legal-move list shrinking; illegal move on occupied cell; illegal move after
game over; each of the 8 winning lines for both marks; winning-line reporting;
draw detection; win-on-last-cell precedence over draw; reset.
