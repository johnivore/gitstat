# Gitstat Changelog

## UNRELEASED

### Changed

* Fx bug where a couple of rare errors were colorized twice


## [0.2.0] 2020-03-06

### Added

* Add more error checking from git commands
* Add more type hints & docstrings

### Changed

* Fix bug where "check --quiet" would always skip ignored repos


## [0.1.1] 2020-03-05

### Changed

* Fix bug where 'showclone' always included ignored repos


## [0.1.0] 2020-03-04

### Added

* Support checking repos that are not tracked by gitstat
* Add a fair amount of type hinting
* Add 'is-tracked' command
* setuptools packaging
* Add '--version'
* Add '--include-ignored' to several commands
* Add '--include-existing' to 'showclone'

### Changed

* Use 'Click' to manage command-line options
* Remove 'update' command (for now?)
* Progress bar now uses tqdm
* For a few commands, replace '--quiet' with '--progress' (so quiet is the default)
* Improve help text
* '--all' now only available for the 'check' command (other commands use '--include-ignored', etc.)


## Initial version - 2018-11

* 'check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch' and 'pull' commands
