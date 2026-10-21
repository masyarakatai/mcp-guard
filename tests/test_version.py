"""The reported version must follow the installed distribution metadata."""

from importlib import metadata, util
from pathlib import Path
from types import ModuleType

import pytest
from click.testing import CliRunner

import mcp_guard
from mcp_guard.cli import main


def _load_package_module() -> ModuleType:
    """Load the initializer without replacing the package used by other tests."""
    assert mcp_guard.__file__ is not None
    spec = util.spec_from_file_location("_mcp_guard_version_test", Path(mcp_guard.__file__))
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_package_version_matches_distribution_metadata() -> None:
    assert mcp_guard.__version__ == metadata.version("mcp-guard-py")


def test_cli_version_matches_distribution_metadata() -> None:
    result = CliRunner().invoke(main, ["--version"], prog_name="mcp-guard")

    assert result.exit_code == 0
    assert result.output.strip().endswith(f", version {metadata.version('mcp-guard-py')}")


def test_version_follows_future_distribution_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def distribution_version(distribution_name: str) -> str:
        assert distribution_name == "mcp-guard-py"
        return "42.0.0rc1"

    monkeypatch.setattr(metadata, "version", distribution_version)

    assert _load_package_module().__version__ == "42.0.0rc1"


def test_version_without_installed_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_distribution(distribution_name: str) -> str:
        assert distribution_name == "mcp-guard-py"
        raise metadata.PackageNotFoundError(distribution_name)

    monkeypatch.setattr(metadata, "version", missing_distribution)

    assert _load_package_module().__version__ == "0.0.0+unknown"
