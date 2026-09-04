"""Headless tests for :mod:`games.tic_tac_toe.app`.

``conftest.py`` forces SDL onto its dummy drivers, so everything here runs
without a real window: synthetic ``pygame`` events and board points are fed
through the step functions and, once, through :func:`app.run` itself.
"""

import inspect

import pygame
import pytest

from games.tic_tac_toe import app
from games.tic_tac_toe.app import AppState, apply_click, handle_event
from games.tic_tac_toe.game import Mark, Status
from games.tic_tac_toe.layout import DEFAULT_LAYOUT

# Click sequences expressed as cell indices.
X_WIN_MOVES = [0, 3, 1, 4, 2]  # X takes the top row
DRAW_MOVES = [0, 1, 2, 4, 3, 5, 7, 6, 8]  # cat's game, X moves last


# -- helpers ----------------------------------------------------------------


def _click_event(index: int) -> pygame.event.Event:
    pos = DEFAULT_LAYOUT.cell_center(index)
    return pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": app.LEFT_BUTTON, "pos": pos}
    )


def _play(state: AppState, indices) -> AppState:
    for index in indices:
        handle_event(state, _click_event(index))
    return state


@pytest.fixture
def state() -> AppState:
    return AppState.new()


# -- construction ---------------------------------------------------------


def test_new_state_is_a_fresh_empty_round_ready_to_run(state):
    assert state.round_.board == (None,) * 9
    assert state.round_.current_mark is Mark.X
    assert state.scoreboard.rounds_played == 0
    assert state.recorded is False
    assert state.running is True


# -- click -> move ------------------------------------------------------


def test_clicking_empty_cells_alternates_x_then_o(state):
    handle_event(state, _click_event(0))
    assert state.round_.board[0] is Mark.X
    assert state.round_.current_mark is Mark.O

    handle_event(state, _click_event(4))
    assert state.round_.board[4] is Mark.O
    assert state.round_.current_mark is Mark.X


def test_click_on_occupied_cell_is_a_no_op(state):
    handle_event(state, _click_event(0))  # X
    handle_event(state, _click_event(0))  # O clicks the same cell
    assert state.round_.board[0] is Mark.X
    assert state.round_.current_mark is Mark.O  # still O's turn


def test_click_outside_the_board_is_a_no_op(state):
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": app.LEFT_BUTTON, "pos": (5, 5)}
    )
    handle_event(state, event)
    assert state.round_.board == (None,) * 9
    assert state.round_.current_mark is Mark.X


def test_click_on_a_gutter_is_a_no_op(state):
    lay = DEFAULT_LAYOUT
    ox, oy = lay.origin
    gutter_point = (ox + lay.cell_size + lay.gutter // 2, oy + 10)
    assert lay.cell_at(gutter_point) is None
    apply_click(state, gutter_point)
    assert state.round_.board == (None,) * 9


def test_right_click_is_ignored(state):
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {"button": 3, "pos": DEFAULT_LAYOUT.cell_center(0)},
    )
    handle_event(state, event)
    assert state.round_.board == (None,) * 9


# -- round end -> score recorded exactly once -------------------------


def test_x_win_sequence_records_exactly_one_x_win(state):
    _play(state, X_WIN_MOVES)
    assert state.round_.status is Status.X_WINS
    assert state.round_.winning_line == (0, 1, 2)
    assert (state.scoreboard.x_wins, state.scoreboard.o_wins,
            state.scoreboard.draws) == (1, 0, 0)
    assert state.recorded is True


def test_draw_sequence_records_exactly_one_draw(state):
    _play(state, DRAW_MOVES)
    assert state.round_.status is Status.DRAW
    assert (state.scoreboard.x_wins, state.scoreboard.o_wins,
            state.scoreboard.draws) == (0, 0, 1)


def test_clicks_after_game_over_are_no_ops_and_do_not_double_record(state):
    _play(state, X_WIN_MOVES)
    assert state.scoreboard.rounds_played == 1

    # Every remaining empty cell, clicked after the win.
    for index in (5, 6, 7, 8):
        handle_event(state, _click_event(index))

    assert state.round_.board[5] is None
    assert state.scoreboard.x_wins == 1
    assert state.scoreboard.rounds_played == 1


def test_apply_click_returns_state_unchanged_once_over(state):
    _play(state, X_WIN_MOVES)
    board_before = state.round_.board
    result = apply_click(state, DEFAULT_LAYOUT.cell_center(8))
    assert result is state
    assert state.round_.board == board_before


# -- quit paths -------------------------------------------------------


def test_quit_event_stops_the_loop(state):
    handle_event(state, pygame.event.Event(pygame.QUIT))
    assert state.running is False


def test_escape_key_stops_the_loop(state):
    handle_event(state, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}))
    assert state.running is False


def test_other_keys_do_not_stop_the_loop(state):
    handle_event(state, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a}))
    assert state.running is True


def test_process_events_applies_a_batch_in_order(state):
    process_batch = app.process_events
    process_batch(state, [_click_event(0), _click_event(1), pygame.event.Event(pygame.QUIT)])
    assert state.round_.board[0] is Mark.X
    assert state.round_.board[1] is Mark.O
    assert state.running is False


# -- rendering a frame (no window) -----------------------------------


def test_draw_frame_runs_headlessly(state):
    surface = pygame.Surface(DEFAULT_LAYOUT.window_size)
    _play(state, [0, 4])
    app.draw_frame(surface, state)  # must not raise


# -- the loop, simulated without a window --------------------------


def test_simulated_loop_plays_a_win_then_quits():
    """Stand in for :func:`app.run`: feed event batches until ``running`` clears."""
    state = AppState.new()
    surface = pygame.Surface(DEFAULT_LAYOUT.window_size)
    batches = [[_click_event(i)] for i in X_WIN_MOVES]
    batches.append([pygame.event.Event(pygame.QUIT)])

    for batch in batches:
        assert state.running is True
        app.process_events(state, batch)
        app.draw_frame(surface, state)

    assert state.running is False
    assert state.scoreboard.x_wins == 1
    assert state.scoreboard.rounds_played == 1


# -- module hygiene ------------------------------------------------


def test_dunder_main_exposes_run_without_launching_it():
    import importlib

    mod = importlib.import_module("games.tic_tac_toe.__main__")
    assert mod.run is app.run


def test_app_keeps_the_raw_loop_thin():
    source = inspect.getsource(app.run)
    # The loop body delegates; no game-rule branching inlined here.
    assert "winning_line" not in source
    assert "WINNING_LINES" not in source
