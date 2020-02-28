# `gitstat` Changelog

## [0.1] UNRELEASED

### Added

* Support checking repos that are not tracked by gitstat
* Add a fair amount of type hinting
* Add 'is-tracked' command

### Changed

* Use 'Click' to manage command-line options
* Remove 'update' command (for now?)
* Progress bar now uses tqdm
* For a few commands, replaced '--quiet' with '--progress'
* Improve help text


## Initial version

* 'check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch' and 'pull' commands
