"""Pure-Python session scorekeeping for Tic-tac-toe.

This module has **no ``pygame`` import**. It tracks the running tally of
completed rounds within a single session: how many rounds ``X`` won, how many
``O`` won, and how many were drawn.

Boundary with the rest of the app
---------------------------------

:class:`ScoreBoard` is deliberately dumb: every call to :meth:`ScoreBoard.record`
adds exactly one to a counter. It does **not** know which :class:`~games.tic_tac_toe.game.Round`
produced a status, and it cannot tell a fresh result from the same result
handed to it twice.

Requirement 10 ("completed rounds update the session score exactly once, at the
moment the round ends") is therefore the *caller's* responsibility, wired up in
ticket 006. The caller must invoke :meth:`record` once per finished round -- for
example on the transition into a terminal status -- and never again while the
result screen lingers.

Persistence to disk is an explicit non-goal: the score lives in memory and is
gone when the app closes.
"""

from __future__ import annotations

from dataclasses import dataclass

from games.tic_tac_toe.game import Status

__all__ = ["ScoreBoard"]

#: Terminal statuses that :meth:`ScoreBoard.record` accepts, mapped to the name
#: of the counter attribute they increment.
_COUNTER_FOR_STATUS: dict[Status, str] = {
    Status.X_WINS: "x_wins",
    Status.O_WINS: "o_wins",
    Status.DRAW: "draws",
}


@dataclass
class ScoreBoard:
    """A running tally of finished rounds in one session.

    The three counters all start at ``0``. :meth:`record` bumps exactly one of
    them per call; :meth:`reset` returns every counter to ``0``.
    """

    x_wins: int = 0
    o_wins: int = 0
    draws: int = 0

    def record(self, status: Status) -> None:
        """Add one to the counter for a finished round's ``status``.

        ``status`` must be one of :attr:`Status.X_WINS <games.tic_tac_toe.game.Status.X_WINS>`,
        :attr:`Status.O_WINS`, or :attr:`Status.DRAW`.

        Raises :class:`ValueError` if handed
        :attr:`Status.IN_PROGRESS <games.tic_tac_toe.game.Status.IN_PROGRESS>`
        (the round is not finished) or any value that is not a
        :class:`~games.tic_tac_toe.game.Status`.
        """
        try:
            counter = _COUNTER_FOR_STATUS[status]
        except (KeyError, TypeError):
            raise ValueError(
                "record() needs a finished-round Status "
                f"(X_WINS, O_WINS or DRAW), got {status!r}"
            ) from None
        setattr(self, counter, getattr(self, counter) + 1)

    @property
    def rounds_played(self) -> int:
        """Total number of finished rounds recorded so far."""
        return self.x_wins + self.o_wins + self.draws

    def reset(self) -> None:
        """Zero all three counters."""
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
