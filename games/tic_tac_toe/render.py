"""Pygame rendering for Tic-tac-toe: surface in, pixels out.

This module introduces ``pygame`` but **not** the event loop. Every function
here takes a target :class:`pygame.Surface` plus plain state and draws onto it.
Nothing here creates a window, flips a screen, reads input, or ticks a clock --
that is ticket 006's job, and deciding game-state transitions belongs to
:mod:`games.tic_tac_toe.game`.

Because nothing here touches a real screen, the whole module runs headless
(``SDL_VIDEODRIVER=dummy``), which is how it is tested.

Geometry (window/board/cell/button rectangles) and the domain enums are reused
as-is from :mod:`games.tic_tac_toe.layout` and :mod:`games.tic_tac_toe.game`;
this module never redefines them.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from games.tic_tac_toe.game import Mark, Round, Status
from games.tic_tac_toe.layout import DEFAULT_LAYOUT, BoardLayout
from games.tic_tac_toe.score import ScoreBoard

__all__ = [
    "Color",
    "Palette",
    "DEFAULT_PALETTE",
    "ViewState",
    "draw",
    "draw_background",
    "draw_grid",
    "draw_marks",
    "draw_turn_indicator",
    "draw_scoreboard",
    "draw_result_banner",
    "draw_winning_line",
    "draw_new_round_button",
]

#: An RGB colour triple.
Color = tuple[int, int, int]


@dataclass(frozen=True)
class Palette:
    """The colours the renderer uses. Immutable; override by passing your own."""

    background: Color = (245, 245, 245)
    grid: Color = (40, 40, 40)
    x_mark: Color = (198, 58, 58)
    o_mark: Color = (46, 92, 196)
    text: Color = (24, 24, 24)
    winning_line: Color = (54, 168, 92)
    button_fill: Color = (58, 118, 198)
    button_text: Color = (248, 248, 248)


#: The palette used when a caller does not supply one.
DEFAULT_PALETTE = Palette()

#: Round-over status -> the banner text shown in place of the turn indicator.
_RESULT_TEXT: dict[Status, str] = {
    Status.X_WINS: "X wins!",
    Status.O_WINS: "O wins!",
    Status.DRAW: "Draw",
}

_MARK_LINE_WIDTH = 8
_WINNING_LINE_WIDTH = 12


@dataclass(frozen=True)
class ViewState:
    """Everything the renderer needs about the current screen, as plain data.

    This is the boundary between game/score logic and drawing: the event loop
    (ticket 006) builds one of these each frame -- see :meth:`from_round` -- and
    hands it to :func:`draw`. The renderer never touches a :class:`Round` or
    :class:`ScoreBoard` directly.
    """

    #: The nine cells, row-major, each ``Mark`` or ``None``.
    board: tuple[Mark | None, ...]
    #: Whose turn it is, or ``None`` once the round is over.
    current_mark: Mark | None
    #: The round status.
    status: Status
    #: Session wins for ``X``.
    x_wins: int
    #: Session wins for ``O``.
    o_wins: int
    #: Session draws.
    draws: int
    #: The three winning-line cell indices, or ``None`` when there is no win.
    winning_line: tuple[int, int, int] | None = None

    @classmethod
    def from_round(cls, round_: Round, scoreboard: ScoreBoard) -> "ViewState":
        """Snapshot a :class:`Round` and :class:`ScoreBoard` into a view state."""
        return cls(
            board=round_.board,
            current_mark=round_.current_mark,
            status=round_.status,
            x_wins=scoreboard.x_wins,
            o_wins=scoreboard.o_wins,
            draws=scoreboard.draws,
            winning_line=round_.winning_line,
        )

    @property
    def is_over(self) -> bool:
        """``True`` once the round is won or drawn."""
        return self.status is not Status.IN_PROGRESS


# -- fonts --------------------------------------------------------------------

_FONT_CACHE: dict[int, "pygame.font.Font"] = {}


def _font(size: int) -> "pygame.font.Font":
    """Return a cached default ``pygame`` font at ``size`` (no font file needed)."""
    if not pygame.font.get_init():
        pygame.font.init()
    font = _FONT_CACHE.get(size)
    if font is None:
        font = pygame.font.Font(None, size)
        _FONT_CACHE[size] = font
    return font


# -- HUD geometry helpers ---------------------------------------------------


def _hud_top(layout: BoardLayout) -> int:
    _, board_y, _, board_h = layout.board_rect
    return board_y + board_h


# -- individual draw functions -------------------------------------------


def draw_background(
    surface: "pygame.Surface", palette: Palette = DEFAULT_PALETTE
) -> None:
    """Fill the whole surface with the background colour."""
    surface.fill(palette.background)


def draw_grid(
    surface: "pygame.Surface",
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw the 3x3 grid: the two vertical and two horizontal gutter bars."""
    board_x, board_y, board_w, board_h = layout.board_rect
    stride = layout.cell_size + layout.gutter
    for step in (0, 1):
        gx = board_x + step * stride + layout.cell_size
        pygame.draw.rect(
            surface, palette.grid, (gx, board_y, layout.gutter, board_h)
        )
        gy = board_y + step * stride + layout.cell_size
        pygame.draw.rect(
            surface, palette.grid, (board_x, gy, board_w, layout.gutter)
        )


def draw_marks(
    surface: "pygame.Surface",
    board: tuple[Mark | None, ...],
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw every ``X`` and ``O`` on ``board`` in its cell; skip empty cells."""
    inset = layout.cell_size // 5
    for index, mark in enumerate(board):
        if mark is None:
            continue
        cell = pygame.Rect(layout.cell_rect(index))
        field = cell.inflate(-2 * inset, -2 * inset)
        if mark is Mark.X:
            pygame.draw.line(
                surface, palette.x_mark, field.topleft, field.bottomright,
                _MARK_LINE_WIDTH,
            )
            pygame.draw.line(
                surface, palette.x_mark, field.bottomleft, field.topright,
                _MARK_LINE_WIDTH,
            )
        else:
            pygame.draw.circle(
                surface, palette.o_mark, cell.center, field.width // 2,
                _MARK_LINE_WIDTH,
            )


def draw_turn_indicator(
    surface: "pygame.Surface",
    current_mark: Mark | None,
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw "X to move" / "O to move". Draws nothing when ``current_mark`` is ``None``."""
    if current_mark is None:
        return
    label = _font(30).render(f"{current_mark.value} to move", True, palette.text)
    surface.blit(label, (layout.origin[0], _hud_top(layout) + 8))


def draw_result_banner(
    surface: "pygame.Surface",
    status: Status,
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw "X wins!" / "O wins!" / "Draw". Draws nothing while in progress."""
    text = _RESULT_TEXT.get(status)
    if text is None:
        return
    label = _font(30).render(text, True, palette.text)
    surface.blit(label, (layout.origin[0], _hud_top(layout) + 8))


def draw_scoreboard(
    surface: "pygame.Surface",
    x_wins: int,
    o_wins: int,
    draws: int,
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw the session tally: ``X`` wins, ``O`` wins and draws, right-aligned."""
    label = _font(24).render(
        f"X {x_wins}   O {o_wins}   Draws {draws}", True, palette.text
    )
    window_w = layout.window_size[0]
    rect = label.get_rect()
    rect.topright = (window_w - layout.origin[0], _hud_top(layout) + 12)
    surface.blit(label, rect)


def draw_winning_line(
    surface: "pygame.Surface",
    winning_line: tuple[int, int, int] | None,
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Highlight the winning line. Draws nothing when ``winning_line`` is ``None``."""
    if winning_line is None:
        return
    start = layout.cell_center(winning_line[0])
    end = layout.cell_center(winning_line[-1])
    pygame.draw.line(
        surface, palette.winning_line, start, end, _WINNING_LINE_WIDTH
    )


def draw_new_round_button(
    surface: "pygame.Surface",
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw the "new round" button using the layout's button rect."""
    rect = pygame.Rect(layout.new_round_rect)
    pygame.draw.rect(surface, palette.button_fill, rect, border_radius=6)
    label = _font(26).render("New round", True, palette.button_text)
    surface.blit(label, label.get_rect(center=rect.center))


def draw(
    surface: "pygame.Surface",
    view_state: ViewState,
    layout: BoardLayout = DEFAULT_LAYOUT,
    palette: Palette = DEFAULT_PALETTE,
) -> None:
    """Draw the whole scene for ``view_state`` onto ``surface``.

    While the round is in progress this shows the turn indicator. Once it is
    over the turn indicator is replaced by the result banner, plus a highlight
    over the winning line when there is one.
    """
    draw_background(surface, palette)
    draw_grid(surface, layout, palette)
    draw_marks(surface, view_state.board, layout, palette)
    if view_state.is_over:
        draw_result_banner(surface, view_state.status, layout, palette)
        draw_winning_line(surface, view_state.winning_line, layout, palette)
    else:
        draw_turn_indicator(surface, view_state.current_mark, layout, palette)
    draw_scoreboard(
        surface, view_state.x_wins, view_state.o_wins, view_state.draws,
        layout, palette,
    )
    draw_new_round_button(surface, layout, palette)
