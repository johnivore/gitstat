#!/usr/bin/fish

# 1. bump version in pyproject.toml
# 2. TODO: check changelog includes notes about this version (?)
# 3. git commit -am 'bumped the version'
# 4. git tag <version>
# 5. git push --tags
# 6. poetry publish ...

if test (count $argv) != 1
    echo "Usage:\n"
    echo "1. Ensure you've updated CHANGELOG for the new version"
    echo "2. Call this script with the same argument you would pass to 'poetry version' (see https://python-poetry.org/docs/cli/#version)"
    exit 1
end

poetry version $argv[1]
set VERSION v(poetry version -s)

git commit -am 'bumped version to $VERSION'
if test $status != 0 ; exit ; end

git tag $VERSION
if test $status != 0 ; exit ; end

git push --tags
if test $status != 0 ; exit ; end

poetry publish --build -r test.pypi.org
if test $status != 0 ; exit ; end

echo "\nSuccess!"
