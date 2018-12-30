# gitstat

## About

`gitstat` is a simple tool to check if your git repos have local changes and succinctly output a summary.  It checks:

* unstaged changes in the working tree
* uncommitted changes in the index
* untracked, unignored files
* unpushed commits
* if a pull from upstream is required

`gitstat` can optionally fetch changes from upstream, and has a few other features to improve the quality of life when dealing with many git repositories.  It uses multiple processes to speed up checks, and will try to continue even if there is a problem with a repository.


## Requirements

* Python 3.5+
* git


## Installation

It's just one Python script, so you could do something like:

```
cp gitstat.py ~/bin/gitstat && chmod +x ~/bin/gitstat
```


## Getting started

### Track a repo

```
gitstat track ~/workspace/myproject
gitstat track .
```

(Relative paths are converted to absolute paths in `gitstat`'s config file.)

Now do something like edit/add files, or commit (but don't push) changes, and run `gitstat` without any options.

### Track a bunch of repos

```
gitstat track ~/workspace/project1 ~/workspace/project2 ...
```

```
find ~/ -type d -name .git -exec gitstat track {} \;
```

(`gitstat` is "smart" enough to know that the parent directory of a directory ending in `/.git` is the actual repository.)

## Usage

Show repos with local/unpushed changes:

```
gitstat
```

Include repos that are up-to-date:

```
gitstat --all
```

Fetch changes from upstream:

```
gitstat --fetch
```

Check only some of your repos:

```
gitstat check /pato/to/repo /path/to/another/repo ...
```

There are more options.  Show help:

```
gitstat --help
```


## Tips & tricks

### Using with scripts

* Similar to `git`, `gitstat --quiet` prints no output (except on error), and returns 1 if there are changes, else 0.
* `gitstat --if-changes-output something` will return "`something`" if there are changes, else nothing.  Unlike`--quiet`, this will return 0 (except on error).  For example, to add an "!" icon to the i3blocks bar if any of your repos have local changes, add the following to `~/.i3blocks.conf`:

```
[gitstat]
command=~/bin/gitstat --if-changes-output "!"
interval=300
```

### Clone missing repos

* `gitstat showclone` will output a list of `git clone` commands for any repos `gitstat` is tracking, but do not exist on the filesystem.
* `gitstat showclone --all` will do it for all tracked git repos whether they exist or not.

### Are you tracking all the repos you want to track?

Passing a path to `gitstat` that it is not tracking will output "`not tracked by gitstat`", so:

```
find ~/ -type d -name .git | xargs gitstat check
```


## Handling upstream URL changes

The normal `gitstat` output will check if the upstream origin URL matches the URL in the `gitstat` config file and print an alert if they don't match.  `gitstat` can automatically update the origin URL in its config with `gitstat update`:

```
gitstat update /path/to/myproject
```

or to update the origin URL for all tracked repos:

```
gitstat update
```


## Config file

The config file, which contains the list of tracked repos, is located at `$XDG_CONFIG_HOME/gitstatrc` (usually `~/.config/gitstatrc`).
