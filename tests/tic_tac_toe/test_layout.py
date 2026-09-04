"""Tests for the pure geometry helpers in :mod:`games.tic_tac_toe.layout`."""

import inspect

import pytest

from games.tic_tac_toe import layout as layout_module
from games.tic_tac_toe.layout import (
    DEFAULT_LAYOUT,
    WINDOW_SIZE,
    BoardLayout,
    cell_at,
    point_in_new_round_button,
)

# A deliberately different layout to prove nothing is hard-coded.
CUSTOM = BoardLayout.build(
    origin=(10, 40),
    cell_size=50,
    gutter=4,
    hud_height=60,
    button_size=(120, 30),
)


# -- module hygiene -----------------------------------------------------


def test_module_does_not_import_pygame():
    source = inspect.getsource(layout_module)
    assert "import pygame" not in source
    assert "from pygame" not in source
    assert not hasattr(layout_module, "pygame")


# -- layout construction ----------------------------------------------


def test_default_layout_dimensions_are_self_consistent():
    lay = DEFAULT_LAYOUT
    assert lay.board_size == 3 * lay.cell_size + 2 * lay.gutter
    origin_x, origin_y = lay.origin
    win_w, win_h = lay.window_size
    # Symmetric side margins, HUD strip below the board.
    assert win_w == origin_x + lay.board_size + origin_x
    assert win_h > origin_y + lay.board_size
    assert WINDOW_SIZE == lay.window_size


def test_board_rect_matches_origin_and_size():
    lay = DEFAULT_LAYOUT
    assert lay.board_rect == (*lay.origin, lay.board_size, lay.board_size)


def test_build_accepts_custom_dimensions():
    assert CUSTOM.origin == (10, 40)
    assert CUSTOM.cell_size == 50
    assert CUSTOM.gutter == 4
    assert CUSTOM.board_size == 3 * 50 + 2 * 4
    assert CUSTOM.new_round_rect[2:] == (120, 30)
    # Button horizontally centred in the window.
    win_w = CUSTOM.window_size[0]
    assert CUSTOM.new_round_rect[0] == (win_w - 120) // 2


def test_layout_is_frozen():
    with pytest.raises(Exception):
        DEFAULT_LAYOUT.cell_size = 999  # type: ignore[misc]


# -- cell rectangles -------------------------------------------------


def test_cell_rects_returns_nine_rects_inside_the_board():
    lay = DEFAULT_LAYOUT
    rects = lay.cell_rects()
    assert len(rects) == 9
    bx, by, bw, bh = lay.board_rect
    for x, y, w, h in rects:
        assert w == h == lay.cell_size
        assert bx <= x and x + w <= bx + bw
        assert by <= y and y + h <= by + bh


def test_cell_rects_do_not_overlap_and_are_gutter_separated():
    lay = DEFAULT_LAYOUT
    rects = lay.cell_rects()
    # Cells 0 and 1 are in the same row: horizontal gap == gutter.
    x0, _, w0, _ = rects[0]
    x1 = rects[1][0]
    assert x1 - (x0 + w0) == lay.gutter
    # Cells 0 and 3 are in the same column: vertical gap == gutter.
    _, y0, _, h0 = rects[0]
    y3 = rects[3][1]
    assert y3 - (y0 + h0) == lay.gutter


@pytest.mark.parametrize("bad_index", [-1, 9, 100])
def test_cell_rect_rejects_out_of_range(bad_index):
    with pytest.raises(IndexError):
        DEFAULT_LAYOUT.cell_rect(bad_index)


@pytest.mark.parametrize("bad_index", [1.0, "0", None, True])
def test_cell_rect_rejects_non_int(bad_index):
    with pytest.raises(TypeError):
        DEFAULT_LAYOUT.cell_rect(bad_index)


# -- cell_at: the centre of every cell -------------------------------


@pytest.mark.parametrize("layout", [DEFAULT_LAYOUT, CUSTOM])
@pytest.mark.parametrize("index", range(9))
def test_cell_center_round_trips_to_its_index(layout, index):
    assert layout.cell_at(layout.cell_center(index)) == index
    assert cell_at(layout.cell_center(index), layout) == index


def test_module_level_cell_at_uses_default_layout():
    for index in range(9):
        assert cell_at(DEFAULT_LAYOUT.cell_center(index)) == index


# -- cell_at: outside the board -------------------------------------


@pytest.mark.parametrize(
    "point",
    [
        (-1, -1),
        (-5, 100),
        (100, -5),
        (5000, 5000),
        (0, 5000),
    ],
)
def test_cell_at_outside_board_is_none(point):
    assert DEFAULT_LAYOUT.cell_at(point) is None
    assert cell_at(point) is None


def test_cell_at_in_the_hud_below_the_board_is_none():
    lay = DEFAULT_LAYOUT
    bx, by, bw, bh = lay.board_rect
    assert lay.cell_at((bx + 5, by + bh + 5)) is None


# -- cell_at: gutters ----------------------------------------------


def test_cell_at_on_a_vertical_gutter_is_none():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    # Just past the right edge of cell 0, inside the gutter before cell 1.
    gutter_x = ox + lay.cell_size + lay.gutter // 2
    assert lay.cell_at((gutter_x, oy + 5)) is None


def test_cell_at_on_a_horizontal_gutter_is_none():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    gutter_y = oy + lay.cell_size + lay.gutter // 2
    assert lay.cell_at((ox + 5, gutter_y)) is None


# -- cell_at: boundary rules (half-open rects) --------------------


def test_top_left_pixel_of_board_maps_to_cell_zero():
    assert DEFAULT_LAYOUT.cell_at(DEFAULT_LAYOUT.origin) == 0


def test_last_pixel_inside_cell_zero_maps_to_cell_zero():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    assert lay.cell_at((ox + lay.cell_size - 1, oy + lay.cell_size - 1)) == 0


def test_first_pixel_of_cell_zeros_right_edge_is_not_cell_zero():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    # x == origin + cell_size is the first gutter pixel, not part of any cell.
    assert lay.cell_at((ox + lay.cell_size, oy + 5)) is None


def test_bottom_right_corner_of_board_is_outside():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    assert lay.cell_at((ox + lay.board_size, oy + lay.board_size)) is None


def test_last_pixel_inside_the_board_maps_to_cell_eight():
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    assert lay.cell_at((ox + lay.board_size - 1, oy + lay.board_size - 1)) == 8


# -- new round button --------------------------------------------


def test_point_in_new_round_button_true_at_center():
    x, y, w, h = DEFAULT_LAYOUT.new_round_rect
    center = (x + w // 2, y + h // 2)
    assert DEFAULT_LAYOUT.point_in_new_round_button(center) is True
    assert point_in_new_round_button(center) is True


def test_point_in_new_round_button_true_at_top_left_pixel():
    x, y, _, _ = DEFAULT_LAYOUT.new_round_rect
    assert DEFAULT_LAYOUT.point_in_new_round_button((x, y)) is True


@pytest.mark.parametrize("dx,dy", [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)])
def test_point_in_new_round_button_false_around_far_corner(dx, dy):
    x, y, w, h = DEFAULT_LAYOUT.new_round_rect
    # (x + w, y + h) is the first pixel *outside* a half-open rect, and every
    # offset from it here is also outside.
    assert point_in_new_round_button((x + w + dx, y + h + dy)) is False


def test_point_in_new_round_button_false_well_outside():
    assert point_in_new_round_button((0, 0)) is False
    assert point_in_new_round_button(WINDOW_SIZE) is False


def test_new_round_button_does_not_overlap_the_board():
    lay = DEFAULT_LAYOUT
    _, by, _, bh = lay.board_rect
    assert lay.new_round_rect[1] >= by + bh
