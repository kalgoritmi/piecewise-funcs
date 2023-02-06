#!/usr/bin/env bash

pip install . mypy pytest

mypy --exclude build/ .

pytest -v .