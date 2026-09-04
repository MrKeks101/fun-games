"""Runnable window for a single hot-seat round of Tic-tac-toe.

This module is the *only* place that owns a real ``pygame`` event loop, a
window, and a clock. It stays deliberately thin: the interesting behaviour
(translating a click into a move, applying it, ending the round, recording the
outcome) lives in small pure-ish step functions that can be unit-tested by
feeding them synthetic events / points -- no display required.

Responsibilities delegated elsewhere and merely wired together here:

* board state, move legality and win/draw detection -- :mod:`games.tic_tac_toe.game`
* session score -- :mod:`games.tic_tac_toe.score`
* pixel -> cell hit testing and window size -- :mod:`games.tic_tac_toe.layout`
* drawing the scene -- :mod:`games.tic_tac_toe.render`

Requirement 10 ("completed rounds update the session score exactly once") is
this module's job: :class:`AppState` carries a ``recorded`` latch so the outcome
is handed to the :class:`~games.tic_tac_toe.score.ScoreBoard` on the single
frame the round becomes terminal and never again.

Requirement 8 ("start a new round at any time") is handled by
:func:`start_new_round`: the on-screen "new round" button and the ``N`` /
``Space`` keys both clear the board and result while leaving the session score
alone, so abandoning a round in progress never touches the tally.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from games.tic_tac_toe.game import IllegalMoveError, Round
from games.tic_tac_toe.layout import DEFAULT_LAYOUT, BoardLayout
from games.tic_tac_toe.render import ViewState, draw
from games.tic_tac_toe.score import ScoreBoard

__all__ = [
    "AppState",
    "handle_event",
    "process_events",
    "apply_click",
    "start_new_round",
    "draw_frame",
    "run",
]

#: Window title.
CAPTION = "Tic-tac-toe"
#: Frame-rate cap for the main loop.
FPS = 60
#: The mouse button that places a mark.
LEFT_BUTTON = 1
#: Keys that start a fresh round (see requirements open question 3).
NEW_ROUND_KEYS = frozenset({pygame.K_n, pygame.K_SPACE})


@dataclass
class AppState:
    """Mutable state threaded through one run of the app.

    ``recorded`` is the latch behind requirement 10: it flips to ``True`` the
    first time a finished round's outcome is pushed onto ``scoreboard`` and
    keeps the result screen from double-counting on later frames.
    """

    round_: Round
    scoreboard: ScoreBoard
    layout: BoardLayout = DEFAULT_LAYOUT
    recorded: bool = False
    running: bool = True

    @classmethod
    def new(cls, layout: BoardLayout = DEFAULT_LAYOUT) -> "AppState":
        """A fresh state: empty round, zeroed scoreboard, loop armed to run."""
        return cls(round_=Round(), scoreboard=ScoreBoard(), layout=layout)


def _record_if_finished(state: AppState) -> None:
    """Record the outcome exactly once, on the transition into a terminal state."""
    if state.round_.is_over and not state.recorded:
        state.scoreboard.record(state.round_.status)
        state.recorded = True


def apply_click(state: AppState, point: tuple[float, float]) -> AppState:
    """Translate a screen click at ``point`` into a move and apply it.

    No-ops (consuming no turn, raising nothing) when the round is already over,
    when ``point`` is outside the board or on a gutter, or when the target cell
    is occupied. On a legal move the mark is placed and -- if that ends the
    round -- the outcome is recorded once.
    """
    if state.round_.is_over:
        return state
    index = state.layout.cell_at(point)
    if index is None:
        return state
    try:
        state.round_.play(index)
    except IllegalMoveError:
        return state
    _record_if_finished(state)
    return state


def start_new_round(state: AppState) -> AppState:
    """Clear the board and result for a fresh round, keeping the session score.

    ``X`` moves first again (requirement 9). The :class:`ScoreBoard` is left
    untouched, so starting a new round mid-play abandons the current one without
    recording anything. ``recorded`` is re-armed so the next finished round is
    counted once.
    """
    state.round_.new_round()
    state.recorded = False
    return state


def handle_event(state: AppState, event: "pygame.event.Event") -> AppState:
    """Apply a single ``pygame`` event to ``state``.

    * ``QUIT`` or the ``Esc`` key clears ``state.running`` so the loop stops.
    * ``N`` / ``Space`` start a fresh round via :func:`start_new_round`.
    * A left-click on the "new round" button starts a fresh round; any other
      left-click is routed through :func:`apply_click`.
    * Everything else is ignored.
    """
    if event.type == pygame.QUIT:
        state.running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            state.running = False
        elif event.key in NEW_ROUND_KEYS:
            start_new_round(state)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
        if state.layout.point_in_new_round_button(event.pos):
            start_new_round(state)
        else:
            apply_click(state, event.pos)
    return state


def process_events(state: AppState, events) -> AppState:
    """Feed a batch of events to :func:`handle_event` in order."""
    for event in events:
        handle_event(state, event)
    return state


def draw_frame(surface: "pygame.Surface", state: AppState) -> None:
    """Render the current ``state`` onto ``surface`` via the pure renderer."""
    view = ViewState.from_round(state.round_, state.scoreboard)
    draw(surface, view, state.layout)


def run(layout: BoardLayout = DEFAULT_LAYOUT) -> None:  # pragma: no cover - real display loop
    """Open the window and play a hot-seat session until the player quits.

    The loop is intentionally trivial: pump events through
    :func:`process_events`, redraw via :func:`draw_frame`, flip, tick the clock.
    All the decision-making lives in the functions above, which are unit-tested
    headlessly. ``pygame.quit()`` runs even if something raises, so closing the
    window never leaves a traceback behind.
    """
    pygame.init()
    try:
        screen = pygame.display.set_mode(layout.window_size)
        pygame.display.set_caption(CAPTION)
        clock = pygame.time.Clock()
        state = AppState.new(layout)
        while state.running:
            process_events(state, pygame.event.get())
            draw_frame(screen, state)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
