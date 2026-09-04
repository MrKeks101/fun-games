"""Pure-Python rules engine for a single round of Tic-tac-toe.

This module has **no ``pygame`` import**. It owns board state, move legality,
and win/draw detection so the rules can be unit-tested without a display.

Board layout: 9 cells indexed ``0..8`` in row-major order, i.e.
``index = row * 3 + col``::

    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
"""

from __future__ import annotations

from enum import Enum

__all__ = [
    "Mark",
    "Status",
    "IllegalMoveError",
    "WINNING_LINES",
    "Round",
]


class Mark(Enum):
    """One of the two marks placed on the board."""

    X = "X"
    O = "O"  # noqa: E741 - "O" is the domain name for this mark

    @property
    def other(self) -> "Mark":
        """The opposing mark."""
        return Mark.O if self is Mark.X else Mark.X

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


class Status(Enum):
    """The status of a round."""

    IN_PROGRESS = "in_progress"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"


#: The 8 lines that win a round: 3 rows, 3 columns, 2 diagonals.
WINNING_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

BOARD_SIZE = 9

_WIN_STATUS = {Mark.X: Status.X_WINS, Mark.O: Status.O_WINS}


class IllegalMoveError(Exception):
    """Raised when a move is not allowed.

    Causes: the cell index is out of range, the cell is already occupied, or
    the round is already over. A rejected move never changes the board or whose
    turn it is.
    """


class Round:
    """A single round of Tic-tac-toe.

    ``X`` always moves first. After a move the engine checks for a completed
    line (a win for the mover) *before* checking for a full board (a draw), so
    the move that fills the last cell can still be the winning move. Once the
    round is won or drawn it is terminal: every further move is rejected.
    """

    def __init__(self) -> None:
        self.new_round()

    # -- construction / reset ------------------------------------------------

    def new_round(self) -> None:
        """Return the round to its start state: empty board, ``X`` to move."""
        self._board: list[Mark | None] = [None] * BOARD_SIZE
        self._current: Mark | None = Mark.X
        self._status: Status = Status.IN_PROGRESS
        self._winning_line: tuple[int, int, int] | None = None

    #: Alias — some callers prefer ``reset``.
    reset = new_round

    # -- read-only state ---------------------------------------------------

    @property
    def board(self) -> tuple[Mark | None, ...]:
        """The board contents as a 9-tuple of ``Mark`` or ``None``."""
        return tuple(self._board)

    @property
    def current_mark(self) -> Mark | None:
        """Whose turn it is, or ``None`` once the round is over."""
        return self._current

    @property
    def status(self) -> Status:
        """The current round status."""
        return self._status

    @property
    def is_over(self) -> bool:
        """``True`` once the round is won or drawn."""
        return self._status is not Status.IN_PROGRESS

    @property
    def winner(self) -> Mark | None:
        """The winning mark, or ``None`` if there is no winner (yet or ever)."""
        if self._status is Status.X_WINS:
            return Mark.X
        if self._status is Status.O_WINS:
            return Mark.O
        return None

    @property
    def winning_line(self) -> tuple[int, int, int] | None:
        """The 3 cell indices of the winning line, or ``None``."""
        return self._winning_line

    @property
    def legal_moves(self) -> tuple[int, ...]:
        """Indices of empty cells; empty once the round is over."""
        if self.is_over:
            return ()
        return tuple(i for i, cell in enumerate(self._board) if cell is None)

    # -- mutation --------------------------------------------------------

    def play(self, index: int) -> None:
        """Place the current mark on cell ``index``.

        Raises :class:`IllegalMoveError` if the round is over, the index is out
        of range ``0..8``, or the cell is occupied. On a legal move the mark is
        placed and either the round ends (win/draw) or the turn passes.
        """
        if self.is_over:
            raise IllegalMoveError("the round is already over")
        if not isinstance(index, int) or isinstance(index, bool):
            raise IllegalMoveError(f"cell index must be an int, got {index!r}")
        if not 0 <= index < BOARD_SIZE:
            raise IllegalMoveError(f"cell index {index} is out of range 0..8")
        if self._board[index] is not None:
            raise IllegalMoveError(f"cell {index} is already occupied")

        mover = self._current
        assert mover is not None  # not over -> someone's turn
        self._board[index] = mover

        line = self._completed_line(mover)
        if line is not None:
            self._status = _WIN_STATUS[mover]
            self._winning_line = line
            self._current = None
        elif all(cell is not None for cell in self._board):
            self._status = Status.DRAW
            self._current = None
        else:
            self._current = mover.other

    # -- helpers --------------------------------------------------------

    def _completed_line(self, mark: Mark) -> tuple[int, int, int] | None:
        for line in WINNING_LINES:
            if all(self._board[i] is mark for i in line):
                return line
        return None

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        cells = "".join(c.value if c else "." for c in self._board)
        return f"<Round {cells!r} status={self._status.value}>"
