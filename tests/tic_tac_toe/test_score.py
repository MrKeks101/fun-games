"""Tests for the pure-Python Tic-tac-toe session scoreboard."""

import inspect

import pytest

from games.tic_tac_toe import score as score_module
from games.tic_tac_toe.game import Status
from games.tic_tac_toe.score import ScoreBoard


# -- module hygiene -------------------------------------------------------


def test_module_does_not_import_pygame():
    source = inspect.getsource(score_module)
    assert "import pygame" not in source
    assert "from pygame" not in source
    assert not hasattr(score_module, "pygame")


# -- initial state ------------------------------------------------------


def test_fresh_scoreboard_is_all_zero():
    board = ScoreBoard()
    assert board.x_wins == 0
    assert board.o_wins == 0
    assert board.draws == 0
    assert board.rounds_played == 0


# -- recording individual outcomes ------------------------------------


def test_recording_x_win_increments_only_x():
    board = ScoreBoard()
    board.record(Status.X_WINS)
    assert (board.x_wins, board.o_wins, board.draws) == (1, 0, 0)


def test_recording_o_win_increments_only_o():
    board = ScoreBoard()
    board.record(Status.O_WINS)
    assert (board.x_wins, board.o_wins, board.draws) == (0, 1, 0)


def test_recording_draw_increments_only_draws():
    board = ScoreBoard()
    board.record(Status.DRAW)
    assert (board.x_wins, board.o_wins, board.draws) == (0, 0, 1)


# -- accumulation ----------------------------------------------------


def test_multiple_records_accumulate():
    board = ScoreBoard()
    for status in [Status.X_WINS, Status.X_WINS, Status.O_WINS, Status.DRAW]:
        board.record(status)
    assert (board.x_wins, board.o_wins, board.draws) == (2, 1, 1)
    assert board.rounds_played == 4


def test_rounds_played_tracks_every_recorded_round():
    board = ScoreBoard()
    assert board.rounds_played == 0
    board.record(Status.O_WINS)
    assert board.rounds_played == 1
    board.record(Status.DRAW)
    assert board.rounds_played == 2


# -- invalid / in-progress status ------------------------------------


def test_recording_in_progress_raises_and_changes_nothing():
    board = ScoreBoard()
    board.record(Status.X_WINS)
    with pytest.raises(ValueError):
        board.record(Status.IN_PROGRESS)
    assert (board.x_wins, board.o_wins, board.draws) == (1, 0, 0)


@pytest.mark.parametrize("bad", ["x_wins", None, 1, Status])
def test_recording_non_status_raises(bad):
    board = ScoreBoard()
    with pytest.raises(ValueError):
        board.record(bad)
    assert board.rounds_played == 0


def test_recording_unhashable_value_raises():
    board = ScoreBoard()
    with pytest.raises(ValueError):
        board.record(["x_wins"])
    assert board.rounds_played == 0


# -- reset ---------------------------------------------------------


def test_reset_zeroes_all_counters():
    board = ScoreBoard()
    for status in [Status.X_WINS, Status.O_WINS, Status.DRAW]:
        board.record(status)
    board.reset()
    assert (board.x_wins, board.o_wins, board.draws) == (0, 0, 0)
    assert board.rounds_played == 0


def test_scoreboard_is_usable_again_after_reset():
    board = ScoreBoard()
    board.record(Status.X_WINS)
    board.reset()
    board.record(Status.DRAW)
    assert (board.x_wins, board.o_wins, board.draws) == (0, 0, 1)


# -- construction convenience --------------------------------------


def test_scoreboard_can_be_constructed_with_starting_counts():
    board = ScoreBoard(x_wins=2, o_wins=1, draws=3)
    assert board.rounds_played == 6
    board.record(Status.X_WINS)
    assert board.x_wins == 3
