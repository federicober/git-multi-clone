import sys
from pathlib import Path

import toml
import typer
from git import GitCommandError, Repo
from pydantic import BaseModel, ValidationError, field_validator

# Initialize Typer app
app = typer.Typer()


# Pydantic model for validation
class ConfigModel(BaseModel):
    directory: Path  # Ensures it's a valid Path, not necessarily existing yet
    repos: dict[str, str]

    @field_validator("directory")
    def check_directory_is_not_a_file(cls, value: Path) -> Path:
        """Ensure that the directory is not an existing file."""
        if value.is_file():
            raise ValueError(f"The directory path '{value}' is an existing file.")
        return value.absolute()


def load_config(config_path: Path) -> ConfigModel:
    """Load and validate the TOML configuration using Pydantic."""
    try:
        # Load the raw TOML data
        raw_config = toml.load(config_path)
        # Validate the data using Pydantic
        return ConfigModel(**raw_config)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    except ValidationError as e:
        raise ValueError(f"Configuration validation error: {e}")


def clone_repo(repo_url: str, clone_path: Path) -> None:
    """Clone a git repository to the target directory using GitPython."""
    try:
        if not clone_path.exists():
            print(f"Cloning {repo_url} into {clone_path}...")
            Repo.clone_from(repo_url, str(clone_path))
            print(f"Successfully cloned {repo_url}")
        else:
            print(f"{repo_url} already exists at {clone_path}, skipping.")
    except GitCommandError as e:
        print(f"Error cloning {repo_url}: {e}")


def run_clone_process(config_path: Path) -> None:
    """Handle the cloning process based on the validated config."""
    # Load and validate the configuration
    config = load_config(config_path)

    # Ensure the directory exists, create it if not
    if not config.directory.exists():
        config.directory.mkdir(parents=True)

    # Iterate through the repos and clone each one
    for repo_name, repo_url in config.repos.items():
        clone_repo(str(repo_url), config.directory / repo_name)


@app.command()
def main(
    config_path: Path = typer.Argument(..., help="Path to the TOML configuration file"),
) -> None:
    """CLI entry point, handles errors and exits the script with a status code."""
    try:
        run_clone_process(config_path)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)  # Exit with code 1 for errors
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit with code 1 for unexpected errors


if __name__ == "__main__":
    app()
