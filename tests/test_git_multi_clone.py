from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from git_multi_clone.cli import app
from git_multi_clone.multi_clone import load_config, main

# Initialize the Typer test runner
runner = CliRunner()


@pytest.fixture
def config_data() -> str:
    """Create a valid TOML configuration file"""
    return """
    directory = "repos"
    [repos]
    repo1 = "https://github.com/repo1.git"
    repo2 = "git@github.com:user/repo2.git"
    """


@pytest.fixture
def config_path(tmp_path: Path, config_data: str) -> Path:
    file_path = tmp_path / "config.toml"
    file_path.write_text(config_data)
    return file_path


@pytest.fixture(autouse=True)
def workdir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    workdir_path = tmp_path / "workdir"
    workdir_path.mkdir()
    monkeypatch.chdir(workdir_path)
    return workdir_path


# Test cases for configuration loading
def test_load_config_valid_file(config_path: Path, workdir: Path) -> None:
    config = load_config(config_path)
    assert config.directory == workdir / "repos"
    assert "repo1" in config.repos
    assert config.repos["repo1"] == "https://github.com/repo1.git"


def test_load_config_invalid_file(tmp_path: Path) -> None:
    # Create an invalid TOML file
    config_data = """
    directory = "repos"
    repos = "not a and dict"
    """
    config_path = tmp_path / "invalid_config.toml"
    config_path.write_text(config_data)

    with pytest.raises(ValueError):
        load_config(config_path)


def test_load_config_invalid_file_directory_already_exists(
    workdir: Path, tmp_path: Path
) -> None:
    workdir.joinpath("repos").write_text("")

    config_data = """
    directory = "repos"

    [repos]
    repo1 = "https://github.com/repo1.git"
    """
    config_path = tmp_path / "invalid_config.toml"
    config_path.write_text(config_data)

    with pytest.raises(ValueError):
        load_config(config_path)


# Test cases for directory creation and cloning
@patch("git_multi_clone.multi_clone.Repo.clone_from")
def test_run_clone_process(
    mock_clone_from: MagicMock, config_path: Path, workdir: Path
) -> None:
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        # Run the cloning process
        main(config_path)

        # Ensure the directory is created if it doesn't exist
        mock_mkdir.assert_called_once_with(parents=True)

        # Ensure GitPython's clone_from is called correctly
        assert mock_clone_from.call_count == 2
        mock_clone_from.assert_any_call(
            "https://github.com/repo1.git", str(workdir / "repos" / "repo1")
        )
        mock_clone_from.assert_any_call(
            "git@github.com:user/repo2.git", str(workdir / "repos" / "repo2")
        )


def test_cli_integration_valid(tmp_path: Path) -> None:
    config_path = tmp_path / "multi-repo.toml"
    config_path.write_text(
        f"""
directory = "{tmp_path}"
[repos]

multi_clone = "git@github.com:federicober/git-multi-clone.git"
"""
    )

    result = runner.invoke(app, [str(config_path)])

    print(result.stdout)
    assert result.exit_code == 0
    assert tmp_path.joinpath("multi_clone/.git").is_dir()
