#!/usr/bin/fish

# setup:
#     poetry add --dev coverage pytest

# run this from the project root
#     ./scripts/test.fish

set PROJECT gitstat

# pytest -v verbose, -s disable output capturing, see https://docs.pytest.org/en/stable/capture.html
coverage run --rcfile "$PWD/pyproject.toml" -m pytest -s -v "$PWD/$PROJECT/tests"
if test $status != 0 ; exit ; end

coverage html --rcfile "$PWD/pyproject.toml"
if test $status != 0 ; exit ; end

coverage report -m
