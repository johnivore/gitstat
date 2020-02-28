# `gitstat` Changelog

## [0.1] UNRELEASED

### Added

* Support checking repos that are not tracked by gitstat
* Add a fair amount of type hinting

### Changed

* Use 'Click' to manage command-line options
* Remove 'update' functionality (for now?)
* Progress bar uses tqdm
* For a few commands, replaced '--quiet' with '--progress'


## Initial version

* 'check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch' and 'pull' functionality
