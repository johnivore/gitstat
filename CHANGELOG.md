# Gitstat Changelog

## [0.4.6] 2021-01-05

### Fixed

* Fix Python version dependency in package information

## [0.4.5] 2021-01-03

### Changed

* Re-add package classifiers not copied from (now-deleted) setup.py

## [0.4.4] 2021-01-03

### Fixed

* Fix `--all`

## [0.4.3] 2021-01-03

### Changed

* Various PEP & packing / publishing fixes

## [0.4.2] 2020-12-10

### Added

* Use Poetry for dependency management
* Add lint & test scripts

### Changed

* Get config directory using Click to support non-Unix-like operating systems

## [0.4.1] 2020-03-26

### Changed

* Fix bug where 'showclone' didn't work correctly
* 'pull' no longer prints paths while pulling (which made the progress bar ugly)

## [0.4.0] 2020-03-17

### Added

* Add ability to customize color and style of output
* Add 'config' command
* Auto-create sample config if it doesn't exist

### Changed

* Split config file into two: one for tracked repos, the other for options (currently just customized colors/styles)

## [0.3.0] 2020-03-14

### Added

* Add `--color/--no-color` options to 'check'

### Changed

* Use [colr](https://github.com/welbornprod/colr) for colorization
* Fix bug where checking for URL mismatch of untracked repos would cause an exception
* Show more help when tracking no repos and no paths specified on command line
* Note an error but continue gracefully when a repo doesn't have an origin

## [0.2.1] 2020-03-10

### Added

* Add rudimentary testing with pytest and tox

### Changed

* Fix bug where a couple of rare errors were colorized twice


## [0.2.0] 2020-03-06

### Added

* Add more error checking from git commands
* Add more type hints & docstrings

### Changed

* Fix bug where 'check --quiet' would always skip ignored repos


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

* Use [Click](https://click.palletsprojects.com/) to manage command-line options
* Remove 'update' command (for now?)
* Progress bar now uses [tqdm](https://github.com/tqdm/tqdm)
* For a few commands, replace '--quiet' with '--progress' (so quiet is the default)
* Improve help text
* '--all' now only available for the 'check' command (other commands use '--include-ignored', etc.)


## Initial version - 2018-11

* 'check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch' and 'pull' commands
