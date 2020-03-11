#!/usr/bin/env python3
"""
gitstat.py

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
"""

import os
import sys
from typing import List, Tuple, Dict, Optional, Union
import subprocess
from multiprocessing import Pool, freeze_support, cpu_count
from itertools import repeat
from pathlib import Path
import configparser
from operator import itemgetter
from textwrap import dedent
import click
from click_default_group import DefaultGroup
from tqdm import tqdm
from . import VERSION

OUTPUT_MESSAGES = {
    'unstaged': '\033[0;33m{}\033[0m'.format('unstaged changes'),
    'uncommitted': '\033[0;33m{}\033[0m'.format('uncommitted changes'),
    'untracked': '\033[0;31m{}\033[0m'.format('untracked files'),
    'unpushed': '\033[0;36m{}\033[0m'.format('unpushed commits'),
    'pull-required': '\033[0;32m{}\033[0m'.format('pull required'),
    'up-to-date': '\033[0;32m{}\033[0m'.format('up to date'),
    'url-mismatch': '\033[0;31m{}\033[0m'.format('URL mismatch'),
    'diverged': '\033[0;31m{}\033[0m'.format('DIVERGED'),
    'error-fetching': '\033[0;31m{}\033[0m'.format('error fetching'),
    'error-pulling': '\033[0;31m{}\033[0m'.format('error pulling'),
    'no-upstream-branch': '\033[0;31m{}\033[0m'.format('no matching upsteam branch'),
    'origin-url-error': '\033[0;31m{}\033[0m'.format('error in origin URL'),
}

config = configparser.ConfigParser()

# -------------------------------------------------


def print_error(message: str, repo_path: str, stdout: Optional[bytes] = None, stderr: Optional[bytes] = None):
    """
    Print an error message (e.g., from subprocess output).

    Args:
        message (str): The message to print
        repo_path (str): The path to the git repo about which this error is regarding
        stdout (bytes): stdout output
        stdout (bytes): stderr output

    Returns: Nothing
    """
    print('\033[0;31m{}{}\033[0m'.format(message, ': {}'.format(repo_path) if repo_path else ''))
    if stdout or stderr:
        if stdout:
            print(stdout.decode().strip())
        if stderr:
            print('\033[0;31m{}\033[0m'.format(stderr.decode().strip()))


def config_filename() -> Path:
    """
    Get the path to our config file.

    Returns: the Path to the config file
    """
    if 'XDG_CONFIG_HOME' in os.environ:
        config_filename = Path(os.environ['XDG_CONFIG_HOME'], 'gitstat.conf')
    else:
        config_filename = Path(Path.home(), '.config', 'gitstat.conf')
    return config_filename


def read_config():
    """
    Read config file into global "config" var.
    """
    global config
    filename = config_filename()
    if filename.is_file():
        config.read(filename)


def write_config():
    """
    Read config file from global "config" var.
    """
    global config
    with open(config_filename(), 'w') as file_writer:
        config.write(file_writer)


def fetch_from_origin(path: str) -> Union[str, int]:
    """
    Fetch from origin.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: the path (str) (because with multithreading we want to display our progress)
        On failure: -1
    """
    result = subprocess.run(['git', 'fetch', '--quiet'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error(path, 'error fetching; "git fetch" output follows:', result.stdout, result.stderr)
        return -1
    return path


def pull_from_origin(path: str) -> Union[str, int]:
    """
    Pull from origin.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: the path (str) (because with multithreading we want to display our progress)
        On failure: -1
    """
    print(f'pulling {path}')
    result = subprocess.run(['git', 'pull', '--quiet'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error(path, 'error fetching; "git pull" output follows:', result.stdout, result.stderr)
        return -1
    return path


def get_local(path: str) -> Union[str, int]:
    """
    Find upstream revision.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: str from "git rev-parse @"
        On failure: -1
    """
    result = subprocess.run(['git', 'rev-parse', '@'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error('error doing "rev-parse @"; aborting', path, result.stdout, result.stderr)
        return -1
    return result.stdout.decode().strip()


def get_remote(path: str) -> Union[Tuple[str, str], int]:
    """
    Find upstream revision.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: A tuple of (remote: str, changes: str)
            changes can indicate if there is no matching upstream branch (or empty string)
        On failure: -1
    """
    upstream = '@{u}'
    result = subprocess.run(['git', 'rev-parse', upstream], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return result.stdout.decode().strip(), ''
        changes = None
    else:
        err = result.stderr.decode().strip()
        if 'no upstream configured' in err:
            # fatal: no upstream configured for branch 'dummy'
            changes = 'no-upstream-branch'
        else:
            print_error('error doing "rev-parse {}"; aborting'.format(upstream), path, result.stdout, result.stderr)
            return -1
    return result.stdout.decode().strip(), changes


def update_index(path: str) -> Union[None, int]:
    """
    Updates the index.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: None
        On failure: -1
    """
    result = subprocess.run(['git', 'update-index', '-q', '--ignore-submodules', '--refresh'], cwd=path)
    if result.returncode != 0:
        print_error('error updating index; aborting', path, result.stdout, result.stderr)
        return -1
    return None


def get_base(path: str) -> Union[str, int]:
    """
    Find as good common ancestors as possible for a merge.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: str representing the base
        On failure: -1
    """
    upstream = '@{u}'
    result = subprocess.run(['git', 'merge-base', '@', upstream],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error('error doing "merge-base @"; aborting', path, result.stdout, result.stderr)
        return -1
    return result.stdout.decode().strip()


def check_unstaged_changes(path: str) -> bool:
    """
    Determine whether there are unstaged changes in the working tree.

    Args:
        path (str): The path to the git repo

    Returns:
        bool: True if there are unstaged changes; else False
    """
    result = subprocess.run(['git', 'diff-files', '--quiet', '--ignore-submodules'], cwd=path)
    return result.returncode != 0


def check_uncommitted_changes(path: str) -> bool:
    """
    Determine whether there are uncommitted changes in the index.

    Args:
        path (str): The path to the git repo

    Returns:
        bool: True if there are uncommitted changes in the index; else False
    """
    result = subprocess.run(['git', 'diff-index', '--cached', '--quiet', 'HEAD', '--ignore-submodules'], cwd=path)
    return result.returncode != 0


def check_untracked_files(path: str) -> bool:
    """
    Determine whether there are untracked files.

    Args:
        path (str): The path to the git repo

    Returns:
        bool: True if there are untracked files; else False
    """
    result = subprocess.run(['git', 'ls-files', '-o', '--exclude-standard'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return True if result.stdout else False


def check_unpushed_commits(path: str) -> bool:
    """
    Determine whether there are unpushed commits.
    Note this just calls "git diff", so this will also return True
    if a pull from origin is required.

    Args:
        path (str): The path to the git repo

    Returns:
        bool: True if there are unpushed commits; else False
    """
    # note, no escaping curly braces here
    result = subprocess.run(['git', 'diff', '--quiet', '@{u}..'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result.returncode != 0


def get_repo_url(path: str) -> Union[str, int]:
    """
    Return the origin URL.

    Args:
        path (str): The path to the git repo

    Returns:
        On success: str representing the origin URL
        On failure: -1
    """
    # get repo URL; return None on error
    result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE, cwd=path)
    if result.returncode != 0:
        print_error('error getting git URL', path)
        return -1
    return result.stdout.decode().strip()


def checkrepo(path: str, even_if_uptodate: bool = False) -> Union[Dict, int, None]:
    """
    Run various checks on a repo to determine its general state.
    if even_if_uptodate == False and there are no changes, return None
    else return a dict of ['path': path, 'changes': List['str']]
    Return the origin URL.

    Args:
        path (str): The path to the git repo
        even_if_uptodate (bool): configure whether to return something even if repo is up-to-date

    Returns:
        On success: a Dict of {'path': path, 'changes': List of str or None})
            If "up-to-date" == False and there are no changes, 'changes' will be None; else 'up-to-date' will
            be included in the list.
        On failure: -1
    """
    changes: List[str] = []
    # check that the origin URL matches our config file
    origin_url = get_repo_url(path)
    if not origin_url:
        print_error('error getting git URL', path)
        changes.append('origin-url-error')
    else:
        # check origin URL matches URL in gitstat config
        if origin_url != config[path]['url']:
            print_error(path, 'origin URL mismatch')
            print('  gitstat: {}'.format(config[path]['url']))
            print('  origin:  {}'.format(origin_url))
            changes.append('url-mismatch')
    # get local, remote, and base revisions
    local = get_local(path)
    if type(local) == int:  # error already printed
        return -1
    remote_result = get_remote(path)
    if type(remote_result) == int:  # error already printed
        return -1
    remote, result = remote_result
    if result:
        # no origin branch
        changes.append(result)
    else:
        # get the base so we can compare it to local to determine if a pull is required
        base = get_base(path)
        if type(base) == int:  # error already printed
            return -1
        # compare local/remote/base revisions
        if local == remote:
            pass  # up-to-date
        elif local == base:
            changes.append('pull-required')
        elif remote == base:
            pass  # need to push - later we'll do a git diff which will catch this and other situations)
        else:
            # diverged - shouldn't ever see this?
            changes.append('diverged')
    result = update_index(path)
    if type(result) == int:  # error already printed
        return -1
    if check_unstaged_changes(path):
        changes.append('unstaged')
    if check_uncommitted_changes(path):
        changes.append('uncommitted')
    if check_untracked_files(path):
        changes.append('untracked')
    # When a pull is required, git-diff will indicate there's a difference, and we should pull first anyway.
    # so skip this check when we need to pull.
    if 'pull-required' not in changes:
        if check_unpushed_commits(path):
            changes.append('unpushed')
    if not changes and even_if_uptodate:
        changes.append('up-to-date')
    # if something changed, return the changes; else nothing
    if changes:
        return {'path': path, 'changes': changes}  # return the path to ease using the result with subprocessing
    return None


def checkrepo_bool(path: str, even_if_uptodate: bool = False) -> Union[bool, int]:
    """
    Returns a bool if there are changes to the repo.
    This is just a wrapper for checkrepo(); it would be faster
    if we do the checks "manually" because we could bail as soon as
    one check indicated there are changes.  But this is simpler.

    Args:
        path (str): The path to the git repo
        even_if_uptodate (bool): configure whether to return something even if repo is up-to-date

    Returns:
        On success: True if changes; else False
        On failure: -1
    """
    result = checkrepo(path)
    if type(result) == int:
        return result  # error
    return False if result is None else True


def get_paths(paths: List[str], include_ignored: bool) -> List[str]:
    """
    Return a list of strings representing zero or more paths to git repos.
    Paths are checked if they exist and if they are git repos.
    If paths is not empty, use them; otherwise, use paths being tracked in config.

    Args:
        path (List[str]): The paths to the git repos
        include_ignored (bool): whether to include repos ignored in the config

    Returns:
        A list of str of paths to git repos
    """
    if not paths:
        paths = [x for x in config.sections() if x != 'DEFAULT']
    new_path_list: List[str] = []
    for path in paths:
        if config.has_section(path) and config[path]['ignore'] == 'true' and not include_ignored:
            continue
        if not os.path.isdir(path):
            print_error('not found', path)
        elif not os.path.isdir(os.path.join(path, '.git')):
            print_error('not a git directory', path)
        else:
            new_path_list.append(path)
    return new_path_list


def check_paths(paths: List[str], include_uptodate: bool, progress_bar: bool) -> List[Dict]:
    """
    return a tuple of tuple representing the output
    """
    output: List[Dict] = []
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(paths), disable=not progress_bar, leave=False) as pbar:
            for result in pool.starmap(checkrepo, zip(paths, repeat(include_uptodate)), chunksize=1):
                pbar.update()
                if result is None:
                    continue
                assert isinstance(result, Dict)
                output.append(result)
    return output


def check_paths_with_exit_code(paths: List[str], include_uptodate: bool, progress_bar: bool) -> int:
    """
    return an int representing the return code with which we should exit:
        0 for no changes
        1 for changes
    """
    exit_code: int = 0
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(paths), disable=not progress_bar, leave=False) as pbar:
            for result in pool.starmap(checkrepo_bool, zip(paths, repeat(include_uptodate)), chunksize=1):
                if type(result) == int:
                    continue  # already printed error
                if result:
                    exit_code = 1
                    pool.terminate()
                    pbar.close()
                    break
    return exit_code


@click.group(cls=DefaultGroup, default='check', default_if_no_args=True)
@click.version_option(version=VERSION)
def cli():
    """
    Succinctly display information about git repositories.

    Gitstat looks for unstaged changes, uncommitted changes, untracked/unignored
    files, unpushed commits, and whether a pull from upstream is required.

    Gitstat can maintain a list of repos about which it will report.
    Use "gitstat track" to add repo(s) to its list.

    If no paths to git repos are specified on the command line, gitstat will show
    information about the repos it is tracking.

    Run "gitstat COMMAND --help" for help about a specific command.
    """
    freeze_support()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('-a', '--all', type=bool, default=False, is_flag=True,
              help='Include repos that are up-to-date.')
@click.option('--include-ignored', type=bool, default=False, is_flag=True,
              help='Include repos set by gitstat to be ignored.')
@click.option('-q', '--quiet', type=bool, default=False, is_flag=True,
              help='Be quiet; return 1 if any repo has changes, else return 0.')
@click.option('-p', '--progress', type=bool, default=False, is_flag=True,
              help='Show progress bar.')
@click.pass_context
def check(ctx: click.Context, path: Tuple[str], all: bool, include_ignored: bool, quiet: bool, progress: bool):
    """
    Check repo(s).
    """
    ctx.ensure_object(dict)
    read_config()
    if not path and len(config.sections()) == 0:
        print(
            dedent("""
            No repos specified and no repos are being tracked.
            Either specify path(s) to git repos on the command line, or
            track repo(s) with "gitstat track /path/to/repo".
            """))
        # show top level help and exit
        ctx.fail(ctx.find_root().get_help())
    if quiet:
        int_result = check_paths_with_exit_code(get_paths(list(path), include_ignored=include_ignored),
                                                include_uptodate=all, progress_bar=progress)
        sys.exit(int_result)
    # everything went as expected!
    result: List[Dict] = check_paths(get_paths(list(path), include_ignored=include_ignored),
                                     include_uptodate=all, progress_bar=progress)
    if result:
        # print the array of {'path': path, 'changes': [changes]}
        width = max(len(x['path']) for x in result)
        for item in sorted(result, key=itemgetter('path')):
            changes = ', '.join(OUTPUT_MESSAGES[i] for i in item['changes']).strip()
            print('{path:{width}} {changes}'.format(path=item['path'], width=width, changes=changes))


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
                required=True)
def track(path: tuple):
    """
    Track repo(s).
    """
    global config
    read_config()
    changed = False
    for track_path in path:
        if track_path.endswith('/.git'):
            track_path = track_path[:-5]
        if track_path in config.sections():
            print_error('already being tracked', track_path)
            continue
        if not os.path.isdir(os.path.join(track_path, '.git')):
            print_error('not a git directory', track_path)
            continue
        url = get_repo_url(track_path)
        if type(url) == int:  # error already printed
            continue
        # add it to config file
        config.add_section(track_path)
        config[track_path]['url'] = url
        changed = True
    if changed:
        write_config()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
                required=True)
def untrack(path: tuple):
    """
    Untrack repo(s).
    """
    global config
    read_config()
    changed = False
    for untrack_path in path:
        if untrack_path not in config.sections():
            print_error('already not being tracked', untrack_path)
            continue
        config.remove_section(untrack_path)
        changed = True
    if changed:
        write_config()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
                required=True)
def ignore(path: tuple):
    """
    Ignore repo(s).
    """
    global config
    read_config()
    changed = False
    for ignore_path in path:
        if ignore_path not in config.sections():
            print_error('not being tracked', ignore_path)
            continue
        if config[ignore_path]['ignore'] == 'true':
            print_error('already ignored', ignore_path)
            return
        config[ignore_path]['ignore'] = 'true'
        changed = True
    if changed:
        write_config()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
                required=True)
def unignore(path: tuple):
    """
    Un-ignore repo(s).
    """
    global config
    read_config()
    changed = False
    for ignore_path in path:
        if ignore_path not in config.sections():
            print_error('not being tracked', ignore_path)
            continue
        if config[ignore_path]['ignore'] == 'false':
            print_error('already un-ignored', ignore_path)
            return
        config[ignore_path]['ignore'] = 'false'
        changed = True
    if changed:
        write_config()


@cli.command()
@click.option('--include-existing', type=bool, default=False, is_flag=True,
              help='Include repos that already exist.')
@click.option('--include-ignored', type=bool, default=False, is_flag=True,
              help='Include repos set by gitstat to be ignored.')
def showclone(include_existing: bool, include_ignored: bool):
    """
    Show "git clone" commands needed to clone missing repos.
    """
    global config
    read_config()
    paths = get_paths([], include_ignored=include_ignored)
    for path in paths:
        if include_existing or not os.path.isdir(os.path.join(path, '.git')):
            print('git clone {} {}'.format(config[path]['url'], path))
    sys.exit()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('--include-ignored', type=bool, default=False, is_flag=True,
              help='Include repos set by gitstat to be ignored.')
@click.option('-p', '--progress', type=bool, default=False, is_flag=True,
              help='Show progress bar.')
def fetch(path: tuple, include_ignored: bool, progress: bool):
    """
    Fetch from origin.
    """
    read_config()
    paths_to_fetch = get_paths(list(path), include_ignored=include_ignored)
    if len(paths_to_fetch) == 0:
        return  # might want to chain commands...
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(paths_to_fetch), disable=not progress, leave=False) as pbar:
            for result in pool.imap_unordered(fetch_from_origin, paths_to_fetch, chunksize=1):
                if type(result) == int:  # error
                    pass
                pbar.update()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('--include-ignored', type=bool, default=False, is_flag=True,
              help='Include repos set by gitstat to be ignored.')
@click.option('-p', '--progress', type=bool, default=False, is_flag=True,
              help='Show progress bar.')
def pull(path: tuple, include_ignored: bool, progress: bool):
    """
    Pull from origin (if no local changes).
    Hint: run "gitstat fetch" first.
    """
    read_config()
    paths_to_check: List[str] = get_paths(list(path), include_ignored=include_ignored)
    if len(paths_to_check) == 0:
        return  # might want to chain commands...
    output = check_paths(paths_to_check, include_uptodate=False, progress_bar=progress)
    paths_to_pull: List[str] = []
    for item in output:
        # only pull from repos with origin changes and no local changes
        if len(item['changes']) == 1 and item['changes'][0] == 'pull-required':
            paths_to_pull.append(item['path'])
    if len(paths_to_pull) == 0:
        sys.exit()
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(paths_to_pull), disable=not progress, leave=False) as pbar:
            for result in pool.imap_unordered(pull_from_origin, paths_to_pull, chunksize=1):
                if type(result) == int:  # error
                    continue
                pbar.write(result)
                pbar.update()


@cli.command()
@click.argument('path', nargs=-1, type=click.Path(file_okay=False, dir_okay=True, resolve_path=True), required=True)
@click.option('-q', '--quiet-if-tracked', type=bool, default=False, is_flag=True,
              help='Don\'t output anything if the repo is being tracked.')
def is_tracked(path: tuple, quiet_if_tracked: bool):
    """
    Show whether one or more repos are tracked by gitstat.
    """
    global config
    read_config()
    for path_to_check in path:
        if path_to_check.endswith('/.git'):
            path_to_check = path_to_check[:-5]
        if path_to_check not in config.sections():
            print_error('not being tracked', path_to_check)
            continue
        if not quiet_if_tracked:
            print_error('is being tracked', path_to_check)
