#!/usr/bin/env python3

from pathlib import Path
from gitstat import gitstat
from gitstat.gitstat import GitStatus
import colr.codes


def test():
    # check each GitStatus has a matching output message
    for status in GitStatus:
        if status not in gitstat.OUTPUT_MESSAGES:
            print('matching message for {} not found.'.format(status))
            assert False
    # check colr styles exist
    print(gitstat.COLOR_STYLES)
    for status in gitstat.COLOR_STYLES:
        if gitstat.COLOR_STYLES[status] not in colr.codes['style']:
            print('invalid colr style: {}'.format(gitstat.COLOR_STYLES[status]))
            assert False


def test_checkrepo():
    test_repo_path = str(Path('../gitstat-tests').resolve())
    result = gitstat.checkrepo(test_repo_path)
    assert result['path'] == test_repo_path
    assert GitStatus.UNTRACKED in result['changes']
    assert GitStatus.UNPUSHED in result['changes']
    assert GitStatus.UNCOMMITTED in result['changes']

    # and check changes to config
    # gitstat.track(test_repo_path)
    # track again (fail)
    # ignore
    # ignore again (fail)
    # unignore
    # unignore again (fail)
    # untrack
    # untrack again (fail)
