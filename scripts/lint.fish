#!/usr/bin/fish

# setup:
#     poetry add --dev isort flake8

# run this from the project root
#     ./scripts/test.fish

#isort --color --diff --settings-path "${BASE_DIR}/pyproject.toml" "${BASE_DIR}"
isort --atomic --settings-path "$PWD/pyproject.toml" "$PWD"

flakehell lint gitstat/
if test $status != 0 ; exit ; end
