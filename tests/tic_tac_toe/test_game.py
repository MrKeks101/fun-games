"""Tests for the pure-Python Tic-tac-toe rules engine."""

import inspect

import pytest

from games.tic_tac_toe import game as game_module
from games.tic_tac_toe.game import (
    WINNING_LINES,
    IllegalMoveError,
    Mark,
    Round,
    Status,
)


def play_sequence(rnd: Round, indices) -> Round:
    """Apply a sequence of moves in order."""
    for index in indices:
        rnd.play(index)
    return rnd


# -- module hygiene -------------------------------------------------------


def test_module_does_not_import_pygame():
    source = inspect.getsource(game_module)
    assert "import pygame" not in source
    assert "from pygame" not in source
    assert not hasattr(game_module, "pygame")


# -- marks --------------------------------------------------------------


def test_mark_other_is_opposing():
    assert Mark.X.other is Mark.O
    assert Mark.O.other is Mark.X


# -- initial state ------------------------------------------------------


def test_fresh_round_initial_state():
    rnd = Round()
    assert rnd.board == (None,) * 9
    assert rnd.current_mark is Mark.X
    assert rnd.status is Status.IN_PROGRESS
    assert rnd.is_over is False
    assert rnd.winner is None
    assert rnd.winning_line is None
    assert sorted(rnd.legal_moves) == list(range(9))
    assert len(rnd.legal_moves) == 9


# -- legal moves ------------------------------------------------------


def test_legal_move_fills_cell_and_flips_turn():
    rnd = Round()
    rnd.play(4)
    assert rnd.board[4] is Mark.X
    assert rnd.current_mark is Mark.O
    rnd.play(0)
    assert rnd.board[0] is Mark.O
    assert rnd.current_mark is Mark.X


def test_turn_alternates_over_several_moves():
    rnd = Round()
    expected = [Mark.X, Mark.O, Mark.X, Mark.O, Mark.X]
    for move, mark in zip([0, 1, 2, 5, 8], expected):
        assert rnd.current_mark is mark
        rnd.play(move)


def test_legal_move_list_shrinks_as_cells_fill():
    rnd = Round()
    for move in [0, 4, 1, 5, 8]:
        before = set(rnd.legal_moves)
        assert move in before
        rnd.play(move)
        after = set(rnd.legal_moves)
        assert after == before - {move}


def test_board_is_immutable_snapshot():
    rnd = Round()
    snapshot = rnd.board
    rnd.play(0)
    assert snapshot == (None,) * 9
    assert isinstance(rnd.board, tuple)


# -- illegal moves ------------------------------------------------------


def test_move_on_occupied_cell_is_rejected_and_changes_nothing():
    rnd = Round()
    rnd.play(4)
    board_before = rnd.board
    turn_before = rnd.current_mark
    with pytest.raises(IllegalMoveError):
        rnd.play(4)
    assert rnd.board == board_before
    assert rnd.current_mark is turn_before


@pytest.mark.parametrize("bad_index", [-1, 9, 100])
def test_move_out_of_range_is_rejected(bad_index):
    rnd = Round()
    with pytest.raises(IllegalMoveError):
        rnd.play(bad_index)
    assert rnd.board == (None,) * 9
    assert rnd.current_mark is Mark.X


@pytest.mark.parametrize("bad_index", [1.5, "0", None, True])
def test_move_with_non_int_index_is_rejected(bad_index):
    rnd = Round()
    with pytest.raises(IllegalMoveError):
        rnd.play(bad_index)
    assert rnd.board == (None,) * 9


def test_move_after_game_over_is_rejected():
    rnd = Round()
    # X wins on the top row.
    play_sequence(rnd, [0, 3, 1, 4, 2])
    assert rnd.status is Status.X_WINS
    board_before = rnd.board
    with pytest.raises(IllegalMoveError):
        rnd.play(5)
    assert rnd.board == board_before
    assert rnd.legal_moves == ()


def test_move_after_draw_is_rejected():
    rnd = Round()
    # Fill the board with no winner: X O X / X O O / O X X
    play_sequence(rnd, [0, 1, 2, 4, 3, 6, 5, 8, 7])
    assert rnd.status is Status.DRAW
    with pytest.raises(IllegalMoveError):
        rnd.play(0)


# -- win detection ----------------------------------------------------


def _game_that_wins_on_line(line, winner):
    """Build a move list so ``winner`` completes ``line``.

    The loser plays on three cells outside the line that do not themselves
    form a line.
    """
    line = list(line)
    others = [i for i in range(9) if i not in line]
    loser_moves = _non_winning_triple(others)
    if winner is Mark.X:
        movers = [line[0], loser_moves[0], line[1], loser_moves[1], line[2]]
    else:
        movers = [
            loser_moves[0],
            line[0],
            loser_moves[1],
            line[1],
            loser_moves[2],
            line[2],
        ]
    return movers


def _non_winning_triple(cells):
    """Pick 3 cells from ``cells`` that are not one of the winning lines."""
    from itertools import combinations

    win_sets = [set(line) for line in WINNING_LINES]
    for triple in combinations(cells, 3):
        if set(triple) not in win_sets:
            return list(triple)
    raise AssertionError("no non-winning triple available")  # pragma: no cover


@pytest.mark.parametrize("line", WINNING_LINES)
@pytest.mark.parametrize("winner", [Mark.X, Mark.O])
def test_every_winning_line_for_both_marks(line, winner):
    rnd = Round()
    play_sequence(rnd, _game_that_wins_on_line(line, winner))
    assert rnd.winner is winner
    assert rnd.status is (Status.X_WINS if winner is Mark.X else Status.O_WINS)
    assert set(rnd.winning_line) == set(line)
    assert rnd.is_over is True
    assert rnd.current_mark is None
    assert rnd.legal_moves == ()


def test_winning_line_is_reported_in_canonical_order():
    rnd = Round()
    play_sequence(rnd, [0, 3, 4, 5, 8])  # X takes the main diagonal
    assert rnd.winning_line == (0, 4, 8)


def test_no_winner_mid_game():
    rnd = Round()
    play_sequence(rnd, [0, 1, 2])
    assert rnd.winner is None
    assert rnd.winning_line is None
    assert rnd.status is Status.IN_PROGRESS


# -- draw -----------------------------------------------------------


def test_full_board_with_no_line_is_a_draw():
    rnd = Round()
    play_sequence(rnd, [4, 0, 8, 5, 3, 6, 2, 1, 7])
    assert rnd.status is Status.DRAW
    assert rnd.is_over is True
    assert rnd.winner is None
    assert rnd.winning_line is None
    assert rnd.current_mark is None
    assert rnd.legal_moves == ()


# -- win-on-last-cell precedence over draw ---------------------------


def test_move_that_fills_last_cell_and_completes_line_is_a_win():
    rnd = Round()
    # Board before the last move (cell 8 empty):
    #   X O O
    #   O X X
    #   O X _
    # X plays 8 -> completes the main diagonal (0, 4, 8).
    play_sequence(rnd, [0, 1, 4, 2, 5, 3, 7, 6])
    assert rnd.legal_moves == (8,)
    rnd.play(8)
    assert rnd.status is Status.X_WINS
    assert rnd.winner is Mark.X
    assert set(rnd.winning_line) == {0, 4, 8}


# -- reset --------------------------------------------------------


def test_new_round_returns_to_start_state():
    rnd = Round()
    play_sequence(rnd, [0, 3, 1, 4, 2])  # X wins
    assert rnd.is_over is True
    rnd.new_round()
    assert rnd.board == (None,) * 9
    assert rnd.current_mark is Mark.X
    assert rnd.status is Status.IN_PROGRESS
    assert rnd.winner is None
    assert rnd.winning_line is None
    assert len(rnd.legal_moves) == 9


def test_reset_alias_matches_new_round():
    rnd = Round()
    play_sequence(rnd, [0, 1, 2, 3])
    rnd.reset()
    assert rnd.board == (None,) * 9
    assert rnd.current_mark is Mark.X
    assert rnd.status is Status.IN_PROGRESS


def test_rounds_are_independent():
    a = Round()
    b = Round()
    a.play(0)
    assert b.board == (None,) * 9
    assert b.current_mark is Mark.X
