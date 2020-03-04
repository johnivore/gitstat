# Gitstat Changelog

## [0.1.0]

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
* For a few commands, replaced '--quiet' with '--progress'
* Improve help text
* '--all' now only available for the 'check' command


## Initial version

* 'check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch' and 'pull' commands
