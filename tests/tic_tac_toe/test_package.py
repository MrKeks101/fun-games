"""Smoke test: the tic-tac-toe package imports cleanly."""

import types


def test_package_imports_cleanly():
    import games.tic_tac_toe as ttt

    assert isinstance(ttt, types.ModuleType)


def test_package_has_docstring():
    import games.tic_tac_toe as ttt

    assert ttt.__doc__ is not None
    assert ttt.__doc__.strip()
