# Tic-tac-toe — Requirements

## Description

A local, offline Tic-tac-toe game for the `fun-games` collection, built as a
standalone Python + `pygame` desktop app. This first iteration is **two-player
hot-seat only**: two humans share one keyboard/mouse and take turns on the same
machine. X always moves first. The app detects wins and draws, shows the result,
and keeps a running score across multiple rounds within a single session.

No AI opponent, no networking, no persistence to disk. Those come later.

## Domain notes

- **Board:** 3x3 grid, 9 cells. Each cell is empty, `X`, or `O`.
- **Turn order:** `X` moves first, then players alternate. Exactly one mark is
  placed per turn, on an empty cell.
- **Win:** the first player to get three of their marks in a line wins
  immediately. There are 8 lines: 3 rows, 3 columns, 2 diagonals.
- **Draw:** all 9 cells are filled and no line was completed ("cat's game").
- **End check order:** after a move, check for a win *before* checking for a
  draw (the move that fills the last cell can also be the winning move).
- **Terminal state is sticky:** once a round is won or drawn, no further moves
  are accepted until a new round is started.
- **Game theory (for context, not this iteration):** Tic-tac-toe is a solved
  game. With perfect play by both sides it is always a draw; the first player
  (`X`) can never lose with optimal play. This matters for a future
  unbeatable-bot ticket (minimax), not here.

## Functional requirements

1. The app launches from the repo root as a desktop window (e.g.
   `python -m games.tic_tac_toe`) and can be closed via the window close
   button and/or the `Esc` key.
2. The board is rendered as a 3x3 grid. Empty cells are visually distinct from
   `X` and `O` cells.
3. The app tracks whose turn it is (`X` or `O`) and shows a visible turn
   indicator while a round is in progress.
4. A player places a mark by clicking an empty cell. Clicking an occupied cell,
   or clicking anywhere once the round is over, does nothing (no turn is
   consumed, no error).
5. After each move the app evaluates the board: if a line is completed the
   round ends in a win for the player who just moved; otherwise if the board is
   full the round ends in a draw; otherwise the turn passes to the other
   player.
6. When a round ends, the app shows the result clearly: which player won, or
   that it was a draw. The winning line should be visually highlighted on a
   win.
7. The app keeps a session score: number of rounds won by `X`, number won by
   `O`, and number of draws. The score is visible on screen at all times.
8. The player can start a new round at any time (via an on-screen control
   and/or a key). Starting a new round clears the board and result but keeps
   the session score.
9. On a new round, `X` moves first again (fixed first-player policy for this
   iteration).
10. Completed rounds update the session score exactly once, at the moment the
    round ends — not again if the result screen lingers.
11. Game-rule logic (board state, move legality, win/draw detection) and score
    logic live in plain Python modules with no `pygame` import, so they are
    unit-testable without a display.

## Non-goals

- No AI / single-player mode. (Separate future feature.)
- No online or LAN multiplayer.
- No saving score, stats, or game history to disk; the score resets when the
  app is closed.
- No board sizes other than 3x3, no "misère" or other rule variants.
- No move undo / takeback, no move timer.
- No animations, sound, themes, or configurable colors beyond what's needed to
  meet the requirements above.
- No account, settings screen, or main menu (beyond a new-round control).

## Open questions

Defaults have been chosen so development is not blocked; the stakeholder can
override any of these.

1. **First-player policy across rounds.** Assumed: `X` always starts every
   round. Alternatives: alternate who starts, or loser-starts. (Default: `X`
   always.)
2. **Draws in the scoreboard.** Assumed: show a draw counter alongside `X` and
   `O` win counts. (Default: yes, show draws.)
3. **New-round trigger.** Assumed: both an on-screen button and a key (e.g.
   `N` / `Space`). Acceptable to ship with just one. (Default: on-screen
   button + `N`.)
4. **Keyboard placement.** Assumed: mouse-click only for placing marks;
   number-key placement (1–9) is out of scope for this iteration.
5. **Window size.** Assumed: fixed-size, non-resizable window sized to fit the
   board plus a HUD area. Exact dimensions are the developer's call.
