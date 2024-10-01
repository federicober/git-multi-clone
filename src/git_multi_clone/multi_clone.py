import logging
from pathlib import Path

import pydantic
import toml
from git import GitCommandError, Repo
from pydantic import BaseModel, ValidationError, field_validator

logger = logging.getLogger(__name__)


class ConfigError(ValueError): ...


class ConfigModel(BaseModel):
    directory: Path = pydantic.Field(default_factory=lambda: Path.cwd())
    repos: dict[str, str]

    @field_validator("directory")
    @classmethod
    def check_directory_is_not_a_file(cls, value: Path) -> Path:
        """Ensure that the directory is not an existing file."""
        if value.is_file():
            raise ValueError(f"The directory path '{value}' is an existing file.")
        return value.absolute()


def load_config(config_path: Path) -> ConfigModel:
    """Load and validate the TOML configuration using Pydantic."""
    try:
        return ConfigModel(**toml.load(config_path))
    except ValidationError as e:
        raise ConfigError("Configuration validation error") from e


def clone_repo(repo_url: str, clone_path: Path) -> None:
    """Clone a git repository to the target directory using GitPython."""
    try:
        if not clone_path.exists():
            logger.info(f"Cloning {repo_url} into {clone_path}...")
            Repo.clone_from(repo_url, str(clone_path))
            logger.info(f"Successfully cloned {repo_url}")
        else:
            logger.info(f"{repo_url} already exists at {clone_path}, skipping.")
    except GitCommandError as e:
        logger.info(f"Error cloning {repo_url}: {e}")
        raise e


def main(config_path: Path) -> None:
    """Validate config and clone directories"""
    config = load_config(config_path)

    if not config.directory.exists():
        config.directory.mkdir(parents=True)

    for repo_name, repo_url in config.repos.items():
        clone_repo(str(repo_url), config.directory / repo_name)
