# 003 — Tic-tac-toe session scorekeeping (pure logic)

**Feature:** [Tic-tac-toe](../requirements/tic-tac-toe.md)
**Branch:** `feat/tic-tac-toe-scorekeeping`
**Depends on:** 002

## Goal

Track the running score across multiple rounds within one session, as plain
Python with **no `pygame` import**.

## Scope

Create `games/tic_tac_toe/score.py` (name is the developer's call) providing a
small score object that:

- holds three counters: `X` wins, `O` wins, draws (all start at 0);
- has a method to record a finished round's outcome, given a round status from
  ticket 002 (`X` wins / `O` wins / draw);
- rejects (or ignores with a clear contract) being handed an "in progress"
  status;
- exposes the three counts for display, and optionally a total-rounds-played
  helper;
- has a `reset` that zeroes all counters (for a future "reset score" control —
  not wired to UI in this ticket).

Recording must be **idempotent per round only in the sense that the caller
controls it** — the score object just adds 1 on each call. The
"count exactly once per round" guarantee (requirement 10) is the app's job in
ticket 006; document that boundary here.

## Out of scope

- Deciding *when* to call record (ticket 006).
- Persistence to disk (explicit non-goal).
- Any UI.

## Acceptance criteria

- [ ] Module has no `import pygame`.
- [ ] New score object reads 0 / 0 / 0.
- [ ] Recording an `X` win increments only the `X` counter; same for `O` and
      draw.
- [ ] Recording an "in progress" status raises or is a documented no-op
      (developer picks; test whichever is chosen).
- [ ] Multiple records accumulate correctly (e.g. X, X, O, draw → 2 / 1 / 1).
- [ ] `reset` returns to 0 / 0 / 0.
- [ ] `pytest --cov=games --cov-fail-under=90` passes.

## Expected tests

`tests/tic_tac_toe/test_score.py` — initial zeros; each outcome increments the
right counter; accumulation across several rounds; invalid/in-progress status
handling; reset.
