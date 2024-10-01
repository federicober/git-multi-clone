import logging
import sys
from pathlib import Path

import typer

from . import multi_clone

app = typer.Typer()


@app.command()
def entrypoint(
    config_path: Path = typer.Argument(
        "git-multi-clone.toml",
        help="Path to the TOML configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
) -> None:
    """Clone git repositories declaratively"""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    try:
        multi_clone.main(config_path)
    except multi_clone.ConfigError as err:
        logging.error(f"{err}")
        raise typer.Abort from err


if __name__ == "__main__":
    app()
