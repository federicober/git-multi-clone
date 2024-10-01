#!/usr/bin/env bash

echo "Installing tools" 
uv pip install --quiet build twine

rm -rf dist/
python -m build --installer uv .

twine upload dist/*
