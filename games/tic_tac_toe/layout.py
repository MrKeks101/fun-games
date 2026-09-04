"""Pure geometry helpers mapping screen pixels to Tic-tac-toe board cells.

This module has **no ``pygame`` import**. It operates on plain numbers and
plain tuples so it can be unit-tested without a display, and so ticket 005
(rendering) and ticket 006 (event loop) can share one source of truth for the
window/board dimensions.

Coordinate system
-----------------

Screen pixels are ``(x, y)`` with the origin at the top-left of the window,
``x`` growing right and ``y`` growing down -- the usual ``pygame`` convention.

Board model
-----------

The board is a square of ``board_size`` pixels whose top-left corner sits at
``origin``. It holds a 3x3 grid of square cells ``cell_size`` pixels wide,
separated (and not surrounded) by grid-line gutters ``gutter`` pixels wide::

    board_size = 3 * cell_size + 2 * gutter

Cells are indexed ``0..8`` in row-major order, matching
:mod:`games.tic_tac_toe.game`::

    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8

so ``index = row * 3 + col``.

Boundary behaviour (defined, not accidental)
--------------------------------------------

Every rectangle in this module is treated as **half-open**: a point belongs to
a rect when ``left <= x < right`` and ``top <= y < bottom``.

* The exact top-left pixel of a cell maps to that cell.
* The pixels along a cell's right/bottom edge belong to the next cell, the
  gutter, or (past the board) to nothing.
* A point on a grid-line gutter maps to ``None`` -- it is not in any cell.
* A point outside the board square maps to ``None``.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "CELL_SIZE",
    "GUTTER",
    "BOARD_ORIGIN",
    "HUD_HEIGHT",
    "NEW_ROUND_BUTTON_SIZE",
    "BoardLayout",
    "DEFAULT_LAYOUT",
    "WINDOW_SIZE",
    "cell_at",
    "point_in_new_round_button",
]

# -- default dimensions (all overridable via ``BoardLayout.build``) ----------

#: Side length of a single cell, in pixels.
CELL_SIZE = 116
#: Width of the grid lines drawn between cells, in pixels.
GUTTER = 6
#: Top-left pixel of the board square within the window.
BOARD_ORIGIN = (20, 20)
#: Height of the HUD strip below the board (turn indicator, score, button).
HUD_HEIGHT = 80
#: ``(width, height)`` of the "new round" button, in pixels.
NEW_ROUND_BUTTON_SIZE = (160, 48)

_GRID = 3


def _in_rect(point: tuple[float, float], rect: tuple[int, int, int, int]) -> bool:
    """Half-open containment: ``left <= x < right`` and ``top <= y < bottom``."""
    x, y = point
    left, top, width, height = rect
    return left <= x < left + width and top <= y < top + height


@dataclass(frozen=True)
class BoardLayout:
    """Immutable description of where the board and its controls sit on screen.

    Build one with :meth:`build` (which applies the module defaults) rather than
    constructing it directly, unless you have already computed every field.
    """

    #: Top-left pixel ``(x, y)`` of the board square.
    origin: tuple[int, int]
    #: Side length of one cell, in pixels.
    cell_size: int
    #: Width of the gutter between two cells, in pixels.
    gutter: int
    #: ``(x, y, width, height)`` of the "new round" button.
    new_round_rect: tuple[int, int, int, int]
    #: ``(width, height)`` of the whole application window.
    window_size: tuple[int, int]

    @classmethod
    def build(
        cls,
        *,
        origin: tuple[int, int] = BOARD_ORIGIN,
        cell_size: int = CELL_SIZE,
        gutter: int = GUTTER,
        hud_height: int = HUD_HEIGHT,
        button_size: tuple[int, int] = NEW_ROUND_BUTTON_SIZE,
    ) -> "BoardLayout":
        """Return a layout, deriving the board square, window and button rect.

        The board square is ``3 * cell_size + 2 * gutter`` on a side. The window
        adds a symmetric margin (equal to ``origin``'s components) on the right
        and a ``hud_height`` strip below the board. The button is centred
        horizontally in the window and vertically within the HUD strip.
        """
        origin_x, origin_y = origin
        board_size = _GRID * cell_size + (_GRID - 1) * gutter

        window_w = origin_x + board_size + origin_x
        window_h = origin_y + board_size + hud_height

        button_w, button_h = button_size
        button_x = (window_w - button_w) // 2
        button_y = origin_y + board_size + (hud_height - button_h) // 2

        return cls(
            origin=origin,
            cell_size=cell_size,
            gutter=gutter,
            new_round_rect=(button_x, button_y, button_w, button_h),
            window_size=(window_w, window_h),
        )

    # -- derived geometry --------------------------------------------------

    @property
    def board_size(self) -> int:
        """Side length of the whole board square, in pixels."""
        return _GRID * self.cell_size + (_GRID - 1) * self.gutter

    @property
    def board_rect(self) -> tuple[int, int, int, int]:
        """``(x, y, width, height)`` of the board square."""
        return (*self.origin, self.board_size, self.board_size)

    def cell_rect(self, index: int) -> tuple[int, int, int, int]:
        """``(x, y, width, height)`` of cell ``index`` (``0..8``)."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"cell index must be an int, got {index!r}")
        if not 0 <= index < _GRID * _GRID:
            raise IndexError(f"cell index {index} is out of range 0..8")
        origin_x, origin_y = self.origin
        stride = self.cell_size + self.gutter
        row, col = divmod(index, _GRID)
        return (
            origin_x + col * stride,
            origin_y + row * stride,
            self.cell_size,
            self.cell_size,
        )

    def cell_rects(self) -> tuple[tuple[int, int, int, int], ...]:
        """The nine cell rects, in index order."""
        return tuple(self.cell_rect(i) for i in range(_GRID * _GRID))

    def cell_center(self, index: int) -> tuple[int, int]:
        """The centre pixel of cell ``index`` (``0..8``)."""
        x, y, width, height = self.cell_rect(index)
        return (x + width // 2, y + height // 2)

    # -- hit testing -----------------------------------------------------

    def cell_at(self, point: tuple[float, float]) -> int | None:
        """Return the cell index ``0..8`` under ``point``, or ``None``.

        ``None`` is returned when ``point`` is outside the board square or on a
        grid-line gutter between cells. See the module docstring for the exact
        (half-open) boundary rules.
        """
        origin_x, origin_y = self.origin
        local_x = point[0] - origin_x
        local_y = point[1] - origin_y

        board_size = self.board_size
        if not (0 <= local_x < board_size and 0 <= local_y < board_size):
            return None

        stride = self.cell_size + self.gutter
        col, col_offset = divmod(int(local_x), stride)
        row, row_offset = divmod(int(local_y), stride)
        if col_offset >= self.cell_size or row_offset >= self.cell_size:
            return None  # on a gutter
        return row * _GRID + col

    def point_in_new_round_button(self, point: tuple[float, float]) -> bool:
        """``True`` when ``point`` lies within the "new round" button rect."""
        return _in_rect(point, self.new_round_rect)


#: The layout used by the app when no custom dimensions are supplied.
DEFAULT_LAYOUT = BoardLayout.build()

#: Convenience alias for the default window size.
WINDOW_SIZE = DEFAULT_LAYOUT.window_size


def cell_at(
    point: tuple[float, float], layout: BoardLayout = DEFAULT_LAYOUT
) -> int | None:
    """Module-level shortcut for :meth:`BoardLayout.cell_at` on ``layout``."""
    return layout.cell_at(point)


def point_in_new_round_button(
    point: tuple[float, float], layout: BoardLayout = DEFAULT_LAYOUT
) -> bool:
    """Module-level shortcut for :meth:`BoardLayout.point_in_new_round_button`."""
    return layout.point_in_new_round_button(point)
