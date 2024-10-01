# Git Multi Clone

`git-multi-clone` is a simple command-line tool to clone multiple Git repositories based on a declarative configuration file.

It uses [GitPython](https://gitpython.readthedocs.io/en/stable/) to handle the repository cloning and [Typer](https://typer.tiangolo.com/) for the command-line interface.

## Features

- Clone multiple Git repositories at once using a TOML configuration file.
- Specify a target directory for all repositories.
- Supports both HTTPS and SSH Git URLs.

## Usage

1. Install using `pip`.

   ```bash
   pip install git-multi-clone
   ```

2. Use the `git-multi-clone` command to clone repositories based on a TOML configuration file.

    ```bash
    git-multi-clone [/path/to/config.toml]
    ```

## Configuration file

The configuration file is a TOML file that specifies the repositories to clone and the target directory. Example `config.toml`:

```toml
directory = "repos"

[repos]
repo1 = "https://github.com/user/repo1.git"
repo2 = "git@github.com:user/repo2.git"
```

- `directory`: The target directory where the repositories will be cloned. If not specified, it defaults to the current working directory.
- `repos`: A dictionary where the keys are the names of the repositories, and the values are the Git URLs.

## License

This project is licensed under the MIT License.
