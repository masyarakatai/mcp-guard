"""Acceptance tests for #117: the reported version must equal pyproject [project] version."""

import importlib.metadata
import importlib.util
import pathlib
import subprocess
import sys

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomllib arrived in 3.11
    import tomli as tomllib

import mcp_guard

_DISTRIBUTION = "mcp-guard-py"


def _pyproject_version() -> str:
    with pathlib.Path("pyproject.toml").open("rb") as fh:
        return str(tomllib.load(fh)["project"]["version"])


def _reload_initializer() -> object:
    spec = importlib.util.spec_from_file_location(
        "_mcp_guard_pin_test", pathlib.Path(mcp_guard.__file__)
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_imported_version_matches_pyproject() -> None:
    assert mcp_guard.__version__ == _pyproject_version()


def test_cli_version_matches_pyproject() -> None:
    out = subprocess.run(
        [sys.executable, "-m", "mcp_guard.cli", "--version"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert _pyproject_version() in out


def test_future_bump_is_reflected_without_touching_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bug class is a manual bump; a bumped dist must be reported as-is."""
    monkeypatch.setattr(importlib.metadata, "version", lambda _name: "42.0.0")
    assert _reload_initializer().__version__ == "42.0.0"


def test_missing_distribution_reports_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(_DISTRIBUTION)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    assert _reload_initializer().__version__ == "0.0.0+unknown"
