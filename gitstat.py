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
from typing import List
import subprocess
from multiprocessing import Pool, freeze_support, cpu_count
from pathlib import Path
import argparse
import configparser
from operator import itemgetter


OUTPUT_MESSAGES = {'unstaged': '\033[0;33m{}\033[0m'.format('unstaged changes'),
                   'uncommitted': '\033[0;33m{}\033[0m'.format('uncommitted changes'),
                   'untracked': '\033[0;31m{}\033[0m'.format('untracked files'),
                   'unpushed': '\033[0;36m{}\033[0m'.format('unpushed commits'),
                   'pull-required': '\033[0;32m{}\033[0m'.format('pull required'),
                   'up-to-date': '\033[0;32m{}\033[0m'.format('up to date'),
                   'url-mismatch': '\033[0;31m{}\033[0m'.format('URL mismatch'),
                   'diverged': '\033[0;31m{}\033[0m'.format('DIVERGED'),
                   'error-fetching': '\033[0;31m{}\033[0m'.format('error fetching'),
                   'error-pulling': '\033[0;31m{}\033[0m'.format('error pulling'),
                   }


# -------------------------------------------------

def print_error(message: str, repo_path=None, stdout=None, stderr=None):
    print('\033[0;31m{}{}\033[0m'.format(message, ': {}'.format(repo_path) if repo_path else ''))
    if stdout or stderr:
        print('output from git follows:')
        if stdout:
            print(stdout.decode().strip())
        if stderr:
            print('\033[0;31m{}\033[0m'.format(stderr.decode().strip()))


def progressbar(iteration: int, total: int, prefix='', suffix='', decimals=0, length=100, blank='-', fill='#'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / total))
    filled_length = int(length * iteration / total)
    prog_bar = fill * filled_length + blank * (length - filled_length)
    print('%s [%s] %s%% %s' % (prefix, prog_bar, percent, suffix), end='\r')


def progress(prefix: str, iteration: int, total: int):
    progressbar(iteration, total, prefix=prefix, suffix='', length=50)


def write_config_file():
    with open(config_filename, 'w') as file_writer:
        config.write(file_writer)


def fetch(path: str):
    result = subprocess.run(['git',
                             'fetch',
                             '--quiet'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error(path, 'error fetching; "git fetch" output follows:', result.stdout, result.stderr)
        return 'error-fetching'


def pull(path: str):
    print('pulling', path)
    result = subprocess.run(['git',
                             'pull',
                             '--quiet'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error(path, 'error fetching; "git pull" output follows:', result.stdout, result.stderr)
        return 'error-pulling'


def get_local(path: str):
    result = subprocess.run(['git',
                             'rev-parse',
                             '@'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error('error doing "rev-parse @"; aborting', path, result.stdout, result.stderr)
        return 1
    return result.stdout.decode().strip()


def get_remote(path: str, upstream='@{u}'):
    # find upstream revision
    # returns (remote, changes)
    result = subprocess.run(['git',
                             'rev-parse',
                             upstream],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode == 0:
        changes = None
    else:
        err = result.stderr.decode().strip()
        if 'no upstream configured' in err:
            # fatal: no upstream configured for branch 'dummy'
            changes = OUTPUT_MESSAGES['pull-required'].format('no matching upstream branch')
        else:
            print_error('error doing "rev-parse {}"; aborting'.format(upstream), path, result.stdout, result.stderr)
            return 1
    return result.stdout.decode().strip(), changes


def update_index(path: str):
    # update the index
    result = subprocess.run(['git',
                             'update-index',
                             '-q',
                             '--ignore-submodules',
                             '--refresh'],
                            cwd=path)
    if result.returncode != 0:
        print_error('error updating index; aborting', path, result.stdout, result.stderr)
        return 1


def get_base(path: str, upstream='@{u}'):
    result = subprocess.run(['git',
                             'merge-base',
                             '@',
                             upstream],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_error('error doing "merge-base @"; aborting', path, result.stdout, result.stderr)
        return 1
    return result.stdout.decode().strip()


def check_unstaged_changes(path: str) -> bool:
    # return True if unstaged changes in the working tree
    result = subprocess.run(['git',
                             'diff-files',
                             '--quiet',
                             '--ignore-submodules'],
                            cwd=path)
    return result.returncode != 0


def check_uncommitted_changes(path: str) -> bool:
    # return True if there are uncommitted changes in the index
    result = subprocess.run(['git',
                             'diff-index',
                             '--cached',
                             '--quiet',
                             'HEAD',
                             '--ignore-submodules'],
                            cwd=path)
    return result.returncode != 0


def check_untracked_files(path: str) -> bool:
    # return True if there are untracked files
    result = subprocess.run(['git',
                             'ls-files',
                             '-o',
                             '--exclude-standard'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return True if result.stdout else False


def check_unpushed_commits(path: str) -> bool:
    # return True if thre are unpushed commits
    # note, no escaping curly braces here
    result = subprocess.run(['git',
                             'diff',
                             '--quiet',
                             '@{u}..'],
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result.returncode != 0


def get_repo_url(path: str) -> str:
    # get repo URL; return None on error
    result = subprocess.run(['git',
                             'config',
                             '--get',
                             'remote.origin.url'],
                            stdout=subprocess.PIPE,
                            cwd=path)
    if result.returncode != 0:
        return None
    return result.stdout.decode().strip()


def checkrepo(path: str) -> List[str]:
    # run various checks on a repo
    # these were previously passed as arguments
    even_if_uptodate = args.all
    return_bool = args.quiet
    changes: List[str] = []
    pull_required = False
    no_upstream_branch = False
    # check that the origin URL matches our config file
    origin_url = get_repo_url(path)
    if not origin_url:
        print_error('error getting git URL', path)
        changes.append(OUTPUT_MESSAGES['untracked'].format('origin URL error'))
    else:
        if origin_url != config[path]['url']:
            print_error(path, 'origin URL mismatch (maybe fix with "gitstat update")')
            print('  gitstat: {}'.format(config[path]['url']))
            print('  origin:  {}'.format(origin_url))
            changes.append('url-mismatch')
    # get local, remote, and base revisions
    local = get_local(path)
    remote, result = get_remote(path)
    if result:
        changes.append(result)
        no_upstream_branch = True
    if not no_upstream_branch:
        base = get_base(path)
        # compare local/remote/base revisions
        if local == remote:
            pass  # up-to-date
        elif local == base:
            changes.append('pull-required')
            pull_required = True
        elif remote == base:
            pass  # need to push - later we'll do a git diff which will catch this and other situations)
        else:
            # diverged - shouldn't ever see this?
            changes.append('diverged')
    update_index(path)
    if check_unstaged_changes(path):
        changes.append('unstaged')
    if check_uncommitted_changes(path):
        changes.append('uncommitted')
    if check_untracked_files(path):
        changes.append('untracked')
    # When a pull is required, git-diff will indicate there's a difference, and we should pull first anyway.
    # so skip this check when we need to pull.
    if not pull_required:
        if check_unpushed_commits(path):
            changes.append('unpushed')
    # --quiet
    if return_bool:
        return True if changes else False
    # --all
    if not changes and even_if_uptodate:
        changes.append('up-to-date')
    # if something changed, return the changes; else nothing
    if changes:
        return {'path': path, 'changes': changes}


def track(path: str):
    # track a repo
    if path in config.sections():
        print_error('already being tracked', path)
        return
    if not os.path.isdir(path):
        print_error('not found', path)
        return
    if not os.path.isdir(os.path.join(path, '.git')):
        print_error('not a git directory', path)
        return
    url = get_repo_url(path)
    if not url:
        print_error('error getting git URL', path)
        return
    # add it to config file
    config.add_section(path)
    config[path]['url'] = url
    write_config_file()


def untrack(path: str):
    # untrack a repo
    if path not in config.sections():
        print_error('already not being tracked', path)
        return
    config.remove_section(path)
    write_config_file()


def ignore(path: str):
    # ignore a repo
    if path not in config.sections():
        print_error('not being tracked', path)
        return
    if config[path]['ignore'] == 'true':
        print_error('already ignored', path)
        return
    config[path]['ignore'] = 'true'
    write_config_file()


def update_url(path: str):
    origin_url = get_repo_url(path)
    if not origin_url:
        print_error('error getting git URL', path)
        return
    if origin_url != config[path]['url']:
        print(path)
        print('  old: {}'.format(config[path]['url']))
        print('  new: {}'.format(origin_url))
        config[path]['url'] = origin_url
        write_config_file()


def fetch_from_origin(paths: List[str], quiet: bool):
    # fetch from upstream
    if not quiet:
        num_processed = 0
        length = len(paths)
        progress('Fetching:', num_processed, length)
    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(fetch, paths, chunksize=1):
            if not quiet:
                num_processed += 1
                progress('Fetching:', num_processed, length)
            if isinstance(result, int) and result == 1:
                # there was an error; terminate threads and exit
                pool.terminate()
                break
            elif isinstance(result, bool) and result:
                if args.quiet:
                    pool.terminate()
                    break
                print_error('should not have reached this point')
                pool.terminate()
                break
    # clear progress bar
    if not quiet:
        print('\r\x1b[2K', end='\r')


def pull_from_origin(paths: List[str]):
    # pull from upstream
    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(pull, paths, chunksize=1):
            if isinstance(result, int) and result == 1:
                # there was an error; terminate threads and exit
                pool.terminate()
                break
            elif isinstance(result, bool) and result:
                if args.quiet:
                    pool.terminate()
                    break
                print_error('should not have reached this point')
                pool.terminate()
                break


# -------------------------------------------------


def main():
    global args
    global config
    global config_filename

    parser = argparse.ArgumentParser(description='Show status of tracked git repos',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('command',
                        nargs='?',
                        default='check',
                        choices=('check', 'track', 'untrack', 'ignore', 'update', 'showclone', 'fetch', 'pull'),
                        help='An optional <command> can be specified:\n'
                             '  check path...     default functionality; check git repos in one or more directories\n'
                             '  track path...     track one more more repos in one or more directories\n'
                             '  untrack path...   untrack one more more repos in one or more directories\n'
                             '  ignore path...    don\'t include one or more directories in future output (but it is still included with "--all")\n'
                             '  update [path...]  update the origin URL in the gitstat config from the origin in git config\n'
                             '                    specify one or more paths, or with no paths specified, update all repos\n'
                             '  showclone         show "git clone" commands needed to clone missing repos (or all repos, with "--all")\n'
                             '                    "showclone" doesn\'t take any paths as arguments\n'
                             '  fetch             fetch from origin\n'
                             '  pull              fetch, then pull if there are no local changes\n'
                        )
    parser.add_argument('path',
                        nargs=argparse.REMAINDER,
                        default=[],
                        help='path1 path2 pathN...')
    parser.add_argument('--all', '-a',
                        action='store_true',
                        default=False,
                        help='show all tracked repos regardless if they have changes')
    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        default=False,
                        help='be quiet; return 1 if any repo has changes, else return 0')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    # get config file location
    if 'XDG_CONFIG_HOME' in os.environ:
        config_filename = Path(os.environ['XDG_CONFIG_HOME'], 'gitstat.conf')
    else:
        config_filename = Path(Path.home(), '.config', 'gitstat.conf')
    if config_filename.is_file():
        config.read(config_filename)

    # add DEFAULT section to config if missing
    if not config.has_section('DEFAULT'):
        config['DEFAULT'] = {'ignore': 'false'}
        write_config_file()

    if args.command == 'showclone' and args.path:
        print_error('"showclone" doesn\'t take any paths as arguments')
        sys.exit(1)

    paths = []
    for p in args.path:
        path = Path(p).absolute()
        # if the user specified the .git path, they surely meant the parent directory
        if path.name == '.git':
            path = path.parent
        paths.append(path)

    if args.command in ['track', 'untrack', 'ignore']:
        if args.command == 'track':
            for p in paths:
                track(str(p))
        if args.command == 'untrack':
            for p in paths:
                untrack(str(p))
        if args.command == 'ignore':
            for p in paths:
                ignore(str(p))
        sys.exit()

    # for all functions after this point, we need to know what repos we're tracking
    tracked_paths = [x for x in config.sections() if x != 'DEFAULT']
    if not tracked_paths:
        print('No git repos are being tracked.')
        print('To track a repo:')
        print('    gitstat track </path/to/myproject>')
        sys.exit()

    # if one or more paths are passed as arguments, use those (instead of all tracked repos)
    if args.path and args.command not in ['update', 'showclone']:
        paths_to_check = []
        for p in paths:
            path = str(p)
            if path in tracked_paths:
                paths_to_check.append(path)
            else:
                print_error('not tracked by gitstat', path)
    else:
        # do all
        paths_to_check = tracked_paths

    if args.command == 'update':
        for path in paths_to_check:
            update_url(path)
        sys.exit()

    if args.command == 'showclone':
        for path in paths_to_check:
            if args.all or not os.path.isdir(os.path.join(path, '.git')):
                print('git clone {} {}'.format(config[path]['url'], path))
        sys.exit()

    # to avoid spawning unneeded processes, do some checks now
    # convert paths we want to check to strings for convenience (config, subprocess, etc.)
    new_path_list: List[str] = []
    for path in paths_to_check:
        if not args.all and config[path]['ignore'] == 'true':
            continue
        if not os.path.isdir(path):
            print_error('not found', path)
        elif not os.path.isdir(os.path.join(path, '.git')):
            print_error('not a git directory', path)
        else:
            new_path_list.append(path)

    if args.command in ['fetch', 'pull']:
        if len(new_path_list) == 0:
            # TODO: print more meaningful message
            print('Nothing to do.')
            sys.exit()
        fetch_from_origin(new_path_list, args.quiet)
        if args.command == 'fetch':
            # if fetching, stop here
            sys.exit()

    # normal functionality
    output = []
    exit_code = None
    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(checkrepo, new_path_list, chunksize=1):
            if isinstance(result, int) and result == 1:
                # there was an error; terminate threads and exit
                exit_code = 1
                pool.terminate()
                break
            elif isinstance(result, bool) and result:
                if args.quiet:
                    exit_code = 1
                    pool.terminate()
                    break
                print_error('should not have reached this point')
                exit_code = 1
                pool.terminate()
                break
            # normal output
            elif result:
                # this repo has changes; add them to the output list
                output.append(result)

    # are we supposed to exit with a specific return code?
    if isinstance(exit_code, int) and exit_code in [0, 1]:
        sys.exit(exit_code)

    if args.command == 'pull':
        paths_to_pull: List[str] = []
        for item in output:
            # only pull from repos with origin changes and no local changes
            if len(item['changes']) == 1 and item['changes'][0] == 'pull-required':
                paths_to_pull.append(item['path'])
        if len(paths_to_pull) == 0:
            sys.exit()
        print('The following repos will be pulled:')
        for path in paths_to_pull:
            print('  {}'.format(path))
        pull_from_origin(paths_to_pull)
        sys.exit()

    # everything went as expected!
    if output:
        # print the array of {'path': path, 'changes': [changes]}
        width = max(len(x['path']) for x in output)
        for item in sorted(output, key=itemgetter('path')):
            print('{path:{width}} {changes}'.format(path=item['path'],
                                                    width=width,
                                                    changes=', '.join(OUTPUT_MESSAGES[i] for i in item['changes'])))

# -------------------------------------------------


if __name__ == '__main__':
    freeze_support()
    main()
