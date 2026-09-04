"""Headless smoke tests for :mod:`games.tic_tac_toe.render`.

These render onto an off-screen surface (see the ``surface`` fixture and
``conftest.py``) and keep their assertions coarse: draw functions must run
without raising and must change pixels where a change is expected. This is a
smoke test, not pixel-perfect snapshotting.
"""

import inspect

import pygame
import pytest

from games.tic_tac_toe import render as render_module
from games.tic_tac_toe.game import Mark, Round, Status
from games.tic_tac_toe.layout import DEFAULT_LAYOUT, BoardLayout
from games.tic_tac_toe.render import (
    DEFAULT_PALETTE,
    Palette,
    ViewState,
    draw,
    draw_background,
    draw_grid,
    draw_marks,
    draw_new_round_button,
    draw_result_banner,
    draw_scoreboard,
    draw_turn_indicator,
    draw_winning_line,
)
from games.tic_tac_toe.score import ScoreBoard

X, O = Mark.X, Mark.O  # noqa: E741 - domain names


# -- helpers -------------------------------------------------------------


def _snapshot(surf: pygame.Surface) -> bytes:
    return pygame.image.tobytes(surf, "RGB")


def _changed(before: bytes, surf: pygame.Surface) -> bool:
    return _snapshot(surf) != before


def _view_state(
    *,
    board=(None,) * 9,
    current_mark=Mark.X,
    status=Status.IN_PROGRESS,
    x_wins=0,
    o_wins=0,
    draws=0,
    winning_line=None,
) -> ViewState:
    return ViewState(
        board=tuple(board),
        current_mark=current_mark,
        status=status,
        x_wins=x_wins,
        o_wins=o_wins,
        draws=draws,
        winning_line=winning_line,
    )


EMPTY = _view_state()

MID_GAME = _view_state(
    board=(X, O, None, None, X, None, None, None, O),
    current_mark=X,
)

X_WIN = _view_state(
    board=(X, X, X, O, O, None, None, None, None),
    current_mark=None,
    status=Status.X_WINS,
    x_wins=1,
    winning_line=(0, 1, 2),
)

O_WIN = _view_state(
    board=(O, O, O, X, X, None, X, None, None),
    current_mark=None,
    status=Status.O_WINS,
    o_wins=1,
    winning_line=(0, 1, 2),
)

DRAW = _view_state(
    board=(X, O, X, X, O, O, O, X, X),
    current_mark=None,
    status=Status.DRAW,
    draws=1,
)

ALL_STATES = {
    "empty": EMPTY,
    "mid_game": MID_GAME,
    "x_win": X_WIN,
    "o_win": O_WIN,
    "draw": DRAW,
}


# -- module hygiene ----------------------------------------------------


def test_render_does_not_use_the_display_or_open_a_window():
    source = inspect.getsource(render_module)
    assert "pygame.display" not in source
    assert "set_mode" not in source
    assert "pygame.event" not in source
    assert "pygame.time" not in source


# -- draw(): every board state renders headlessly ---------------------


@pytest.mark.parametrize("name", list(ALL_STATES))
def test_draw_runs_and_paints_something_for_every_state(surface, name):
    draw(surface, ALL_STATES[name])
    pixels = {surface.get_at((x, y))[:3]
              for x in range(0, surface.get_width(), 7)
              for y in range(0, surface.get_height(), 7)}
    # More than just the background colour ended up on screen.
    assert pixels != {DEFAULT_PALETTE.background}
    assert len(pixels) > 1


@pytest.mark.parametrize("name", list(ALL_STATES))
def test_every_draw_function_runs_headlessly_for_every_state(surface, name):
    state = ALL_STATES[name]
    before = _snapshot(surface)
    draw_background(surface)
    draw_grid(surface)
    draw_marks(surface, state.board)
    draw_turn_indicator(surface, state.current_mark)
    draw_result_banner(surface, state.status)
    draw_scoreboard(surface, state.x_wins, state.o_wins, state.draws)
    draw_winning_line(surface, state.winning_line)
    draw_new_round_button(surface)
    assert _changed(before, surface)


# -- grid -----------------------------------------------------------


def test_draw_grid_paints_a_gutter_pixel(surface):
    draw_background(surface)
    draw_grid(surface)
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    gutter_x = ox + lay.cell_size + lay.gutter // 2
    assert surface.get_at((gutter_x, oy + 5))[:3] == DEFAULT_PALETTE.grid


# -- marks --------------------------------------------------------


def test_draw_marks_fills_occupied_cells_and_leaves_empty_ones(surface):
    draw_background(surface)
    board = (X, None, O, None, None, None, None, None, None)
    draw_marks(surface, board)
    lay = DEFAULT_LAYOUT
    bg = DEFAULT_PALETTE.background

    def cell_touched(index: int) -> bool:
        cx, cy, w, h = lay.cell_rect(index)
        return any(
            surface.get_at((x, y))[:3] != bg
            for x in range(cx, cx + w, 4)
            for y in range(cy, cy + h, 4)
        )

    assert cell_touched(0)  # X
    assert cell_touched(2)  # O
    assert not cell_touched(4)  # still empty


def test_draw_marks_uses_distinct_colours_for_x_and_o(surface):
    draw_background(surface)
    draw_marks(surface, (X, O, None, None, None, None, None, None, None))
    lay = DEFAULT_LAYOUT
    bg = DEFAULT_PALETTE.background

    def colours_in(index: int) -> set:
        cx, cy, w, h = lay.cell_rect(index)
        return {
            surface.get_at((x, y))[:3]
            for x in range(cx, cx + w, 3)
            for y in range(cy, cy + h, 3)
        } - {bg}

    assert DEFAULT_PALETTE.x_mark in colours_in(0)
    assert DEFAULT_PALETTE.o_mark in colours_in(1)


# -- turn indicator vs result banner --------------------------------


def test_turn_indicator_draws_for_a_player_and_not_for_none(surface):
    before = _snapshot(surface)
    draw_turn_indicator(surface, None)
    assert not _changed(before, surface)

    draw_turn_indicator(surface, Mark.X)
    assert _changed(before, surface)


def test_result_banner_draws_when_over_and_not_while_in_progress(surface):
    before = _snapshot(surface)
    draw_result_banner(surface, Status.IN_PROGRESS)
    assert not _changed(before, surface)

    draw_result_banner(surface, Status.X_WINS)
    assert _changed(before, surface)


@pytest.mark.parametrize("status", [Status.X_WINS, Status.O_WINS, Status.DRAW])
def test_result_banner_renders_each_terminal_status(surface, status):
    before = _snapshot(surface)
    draw_result_banner(surface, status)
    assert _changed(before, surface)


def test_draw_shows_turn_indicator_while_in_progress(surface, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(render_module, "draw_turn_indicator",
                        lambda *a, **k: calls.append("turn"))
    monkeypatch.setattr(render_module, "draw_result_banner",
                        lambda *a, **k: calls.append("banner"))
    draw(surface, EMPTY)
    assert calls == ["turn"]


def test_draw_shows_result_banner_not_turn_indicator_once_over(surface, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(render_module, "draw_turn_indicator",
                        lambda *a, **k: calls.append("turn"))
    monkeypatch.setattr(render_module, "draw_result_banner",
                        lambda *a, **k: calls.append("banner"))
    draw(surface, X_WIN)
    assert calls == ["banner"]


# -- scoreboard -------------------------------------------------


def test_scoreboard_renders_the_three_values_it_is_given(surface):
    before = _snapshot(surface)
    draw_scoreboard(surface, 2, 3, 4)
    assert _changed(before, surface)


def test_scoreboard_pixels_differ_when_the_values_differ(surface):
    other = surface.copy()
    draw_scoreboard(surface, 0, 0, 0)
    draw_scoreboard(other, 9, 8, 7)
    assert _snapshot(surface) != _snapshot(other)


# -- winning-line highlight ----------------------------------


def test_winning_line_highlight_only_drawn_when_supplied(surface):
    before = _snapshot(surface)
    draw_winning_line(surface, None)
    assert not _changed(before, surface)

    draw_winning_line(surface, (0, 4, 8))
    assert _changed(before, surface)


def test_draw_skips_the_highlight_for_a_draw_result(surface, monkeypatch):
    seen: list = []
    monkeypatch.setattr(render_module, "draw_winning_line",
                        lambda surf, line, *a, **k: seen.append(line))
    draw(surface, DRAW)
    assert seen == [None]


def test_draw_passes_the_winning_line_through_on_a_win(surface, monkeypatch):
    seen: list = []
    monkeypatch.setattr(render_module, "draw_winning_line",
                        lambda surf, line, *a, **k: seen.append(line))
    draw(surface, X_WIN)
    assert seen == [(0, 1, 2)]


# -- new round button --------------------------------------


def test_new_round_button_is_painted_within_its_rect(surface):
    draw_background(surface)
    draw_new_round_button(surface)
    bx, by, bw, bh = DEFAULT_LAYOUT.new_round_rect
    center = surface.get_at((bx + bw // 2, by + bh // 2))[:3]
    assert center == DEFAULT_PALETTE.button_fill


# -- custom layout / palette are honoured ------------------


def test_draw_accepts_a_custom_layout_and_palette():
    layout = BoardLayout.build(
        origin=(8, 8), cell_size=40, gutter=3, hud_height=50,
        button_size=(90, 24),
    )
    palette = Palette(background=(10, 20, 30))
    surf = pygame.Surface(layout.window_size)
    surf.fill((0, 0, 0))
    draw(surf, MID_GAME, layout, palette)
    # Background colour from the custom palette is present somewhere.
    seen = {surf.get_at((x, y))[:3]
            for x in range(0, surf.get_width(), 5)
            for y in range(0, surf.get_height(), 5)}
    assert (10, 20, 30) in seen


# -- ViewState -------------------------------------------


def test_view_state_is_over_reflects_status():
    assert _view_state(status=Status.IN_PROGRESS).is_over is False
    assert _view_state(status=Status.X_WINS).is_over is True
    assert _view_state(status=Status.DRAW).is_over is True


def test_view_state_from_round_snapshots_round_and_scoreboard():
    rnd = Round()
    rnd.play(0)  # X
    rnd.play(3)  # O
    rnd.play(1)  # X
    rnd.play(4)  # O
    rnd.play(2)  # X wins top row
    board = ScoreBoard()
    board.record(rnd.status)

    view = ViewState.from_round(rnd, board)
    assert view.board == rnd.board
    assert view.current_mark is None
    assert view.status is Status.X_WINS
    assert view.winning_line == (0, 1, 2)
    assert (view.x_wins, view.o_wins, view.draws) == (1, 0, 0)
    assert view.is_over is True


def test_view_state_from_round_mid_game_keeps_current_mark():
    rnd = Round()
    rnd.play(0)
    view = ViewState.from_round(rnd, ScoreBoard())
    assert view.current_mark is Mark.O
    assert view.winning_line is None
    assert view.is_over is False


# -- font cache ----------------------------------------


def test_font_helper_caches_by_size():
    first = render_module._font(22)
    second = render_module._font(22)
    assert first is second
