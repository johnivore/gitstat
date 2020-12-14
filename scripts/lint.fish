#!/usr/bin/fish

# setup:
#     poetry add --dev isort flake8

# run this from the project root
#     ./scripts/test.fish

flake8 $PWD
if test $status != 0 ; exit ; end

isort --atomic --settings-path "$PWD/pyproject.toml" "$PWD"
#isort --color --diff --settings-path "${BASE_DIR}/pyproject.toml" "${BASE_DIR}"
