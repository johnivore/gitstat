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

`gitstat` can also fetch or pull changes from upstream, and has a few other features to improve quality of life
when dealing with many git repositories.  It uses multiple processes to speed things up, and will try to continue
even if there is a problem with a repository.


## Installation

    git clone https://gitlab.com/johnivore/gitstat.git
    pip install --user gitstat/


## Quick start

### Show information about a repository

    gitstat ~/myproject

Note: this is the same as:

    gitstat check ~/myproject

("check" is the default gitstat command.)

You use `~/myproject` all the time; let's tell gitstat to remember it:

    gitstat track ~/myproject

Now do something like edit/add files in `~/myproject`, or commit (but don't push) changes, and run `gitstat` without any options:

    gitstat

By default, `gitstat` will only output repos with changes.  To include repos that are up-to-date:

    gitstat --all

`gitstat` can fetch from origin:

    gitstat fetch

Note that all commands support specifying one or more paths on the command line; for example:

    gitstat fetch ~/myproject ~/work/proj2 ...

Pull from origin:

    gitstat pull

Note that `gitstat` will pull only if there are no local changes and if a pull from upstream is required.  You can run `gitstat fetch` to fetch first.

`gitstat` can do more.  To get help with individual commands:

    gitstat --help
    gitstat check --help


## Tips & tricks

### Using with scripts

Similar to `git`, `gitstat --quiet` prints no output (except on error), and returns 1 if there are changes, else 0.

### Clone missing repos

If moving to a new computer, or sharing `gitstat`'s config between multiple computers, `gitstat showclone` can be used to output a list of `git clone` commands for any repos `gitstat` is tracking, but do not exist on the filesystem.  Then you can copy and paste the output to clone any missing repos.

### Track every repo in your home directory

    find ~/ -type d -name .git -exec gitstat track {} \;

(`gitstat` is "smart" enough to know that the parent directory of a directory named `.git` is the actual repository.)

### Are you tracking all the repos you want to track?

    find ~/ -type d -name .git | xargs gitstat is-tracked --quiet-if-tracked


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
