# Tic-tac-toe

A local, offline two-player hot-seat Tic-tac-toe game (Python + `pygame`) for the
`fun-games` collection. See [`docs/requirements/tic-tac-toe.md`](../../docs/requirements/tic-tac-toe.md).

## How to run

From the repo root, with the project dependencies installed (see
[`PROJECT.md`](../../PROJECT.md) for setup):

```
python -m games.tic_tac_toe
```

## Controls

- **Left click** an empty cell to place your mark (`X` moves first, then players
  alternate).
- **`N`** or **`Space`**, or the on-screen **New round** button — start a fresh
  round. The board and result clear; the session score is kept.
- **`Esc`** or the window close button — quit.

The scoreboard (`X` wins / `O` wins / draws) is shown on screen at all times.
Score is session-only: it is not saved to disk and resets to `0 / 0 / 0` every
time the app is launched.
