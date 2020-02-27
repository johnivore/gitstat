# gitstat

## About

`gitstat` is a simple tool to check if your git repos have local changes and succinctly output a summary.

![(screenshot)](images/screenshots/screenshot.png?raw=true "Basic usage")

`gitstat` finds:

* unstaged changes in the working tree
* uncommitted changes in the index
* untracked, unignored files
* unpushed commits
* if a pull from upstream is required

`gitstat` can optionally fetch or pull changes from upstream, and has a few other features to improve quality of life when dealing with many git repositories.  It uses multiple processes to speed things up, and will try to continue even if there is a problem with a repository.


## Requirements

* Python 3.5+ (currently tested with 3.8)
* click
* git


## Installation

It's just one Python script, so you could do something like:

    cp gitstat.py ~/bin/gitstat && chmod +x ~/bin/gitstat


## Getting started

### Track a repo

    gitstat track ~/workspace/myproject

(Relative paths are converted to absolute paths in `gitstat`'s config file.)

Now do something like edit/add files, or commit (but don't push) changes, and run `gitstat` without any options.

### Track a bunch of repos

    gitstat track ~/workspace/project1 ~/workspace/project2 ...

### Track every repo in your home directory

    find ~/ -type d -name .git -exec gitstat track {} \;

(`gitstat` is "smart" enough to know that the parent directory of a directory named `.git` is the actual repository.)


## Usage

Show repos with local/unpushed changes:

    gitstat

Include repos that are up-to-date:

    gitstat --all

Fetch from upstream:

    gitstat fetch

Fetch from upstream, then pull (if there are no local changes):

    gitstat pull

Check only some of your repos:

    gitstat check /pato/to/repo /path/to/another/repo ...

There are more options.  Show help:

    gitstat --help


## Tips & tricks

### Using with scripts

* Similar to `git`, `gitstat --quiet` prints no output (except on error), and returns 1 if there are changes, else 0.

### Clone missing repos

* `gitstat showclone` will output a list of `git clone` commands for any repos `gitstat` is tracking, but do not exist on the filesystem.
* `gitstat showclone --all` will do it for all tracked git repos whether they exist or not.

### Are you tracking all the repos you want to track?

Passing a path to `gitstat` that it is not tracking will output "`not tracked by gitstat`", so:

    find ~/ -type d -name .git | xargs gitstat check


## Handling upstream URL changes

The normal `gitstat` output will check if the upstream origin URL matches the URL in the `gitstat` config file and print an alert if they don't match.  `gitstat` can automatically update the origin URL in its config with `gitstat update`:

    gitstat update /path/to/myproject

or to update the origin URL for all tracked repos:

    gitstat update


## Config file

The config file, which contains the list of tracked repos, is located at `$XDG_CONFIG_HOME/gitstat.conf` (usually `~/.config/gitstat.conf`).


## License

```
Copyright 2019-2020  John Begenisich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
