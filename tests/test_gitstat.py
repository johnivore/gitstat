#!/usr/bin/env python3

from gitstat import gitstat


def test_checkrepo():
    result = gitstat.checkrepo('../gitstat-tests')
    assert result['path'] == '../gitstat-tests'
    assert 'untracked' in result['changes']
    assert 'unpushed' in result['changes']
    assert 'uncommitted' in result['changes']
