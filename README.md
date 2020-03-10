# gitstat

## About

![(screenshot)](images/screenshots/screenshot.png?raw=true "Basic usage")

```
Usage: gitstat [OPTIONS] COMMAND [ARGS]...

  Succinctly display information about git repositories. Gitstat looks for
  unstaged changes, uncommitted changes, untracked/unignored files, unpushed
  commits, and whether a pull from upstream is required.

  If no paths are specified on the command line, gitstat will show
  information about repos it is tracking. (Use "gitstat track" to track
  repo(s).)

  Run "gitstat COMMAND --help" for help about a specific command.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  check*      Check repo(s).
  fetch       Fetch from origin.
  ignore      Ignore repo(s).
  is-tracked  Show whether one or more repos are tracked by gitstat.
  pull        Pull from origin (if no local changes).
  showclone   Show "git clone" commands needed to clone missing repos.
  track       Track repo(s).
  unignore    Un-ignore repo(s).
  untrack     Untrack repo(s).
```

Gitstat has been designed with being careful in mind.
Gitstat makes no changes to git repos, except for the 'fetch' and 'pull' commands. (`gitstat fetch` simply runs `git fetch`,
and `gitstat pull` will pull from origin *only if* there are no local changes and a pull is required.)


## Installation

    git clone https://gitlab.com/johnivore/gitstat.git
    pip install --user gitstat/


## Quick start

Show information about a repository:

    gitstat ~/myproject

Note that this is the same as:

    gitstat check ~/myproject

("check" is the default command.)

You use `~/myproject` all the time; let's tell gitstat to remember it:

    gitstat track ~/myproject

Now when you run Gitstat with no parameters, it will include the status of `~/myproject`.

Try editing/adding files in `~/myproject`, and/or commit (but don't push) changes, and run Gitstat again:

    gitstat

By default, Gitstat will only output repos with changes.  To include repos that are up-to-date:

    gitstat --all

Gitstat can fetch from origin:

    gitstat fetch

Pull from origin:

    gitstat pull

Gitstat will pull only if there are no local changes and if a pull from upstream is required.  You can run `gitstat fetch` to fetch first.

Gitstat can do more.  To get help with individual commands:

    gitstat --help
    gitstat check --help


## Tips & tricks

### Using with scripts

Similar to `git`, `gitstat --quiet` prints no output (except on error), and returns 1 if there are changes, else 0.

### Clone missing repos

If moving to a new computer, or sharing Gitstat's config between multiple computers, `gitstat showclone` can be used to output a list of `git clone` commands for any repos Gitstat is tracking, but do not exist on the filesystem.  Then you can copy and paste the output to clone any missing repos.

### Track every repo in your home directory

    find ~/ -type d -name .git -exec gitstat track {} \;

(Gitstat is "smart" enough to know that the parent directory of a directory named `.git` is the actual repository.)

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
