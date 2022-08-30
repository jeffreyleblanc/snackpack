#! /usr/bin/env python3

# Python
from pathlib import Path
import json
import shutil
from dataclasses import dataclass, field
from typing import List
import argparse
# Dependencies
import toml

#-- RichPrinter --------------------------------------------------------------------------------------#

import textwrap
from os import get_terminal_size
from math import floor,ceil
import pprint

class SnackPrinter:

    def __init__(self):
        s = get_terminal_size()
        self.NCOLS = s.columns
        self.NROWS = s.lines

    def p(self, text=''):
        print(text)

    def red(self, text):
        print(f"\x1b[31m{text}\x1b[0m")

    def blue(self, text):
        print(f"\x1b[38;5;27m{text}\x1b[0m")

    def cyan(self, text):
        print(f"\x1b[36m{text}\x1b[0m")

    def redbold(self, text):
        print(f"\x1b[31;1m{text}\x1b[0m")

    def green(self, text):
        print(f"\x1b[92m{text}\x1b[0m")

    def gray(self, text):
        print(f"\x1b[38;5;239m{text}\x1b[0m")

    def indent(self, text, indent=4):
        return textwrap.indent(text, prefix=' '*indent)

    def hr(self, char='=', newline=False):
        line = char*self.NCOLS
        return ( f'\n{line}\n' if newline else line )

    def center(self, text, pad=None, newline=False):
        tl = len(text)
        n = 0.5 * ( self.NCOLS - tl )
        if pad is None:
            line = f'{" "*floor(n)}{text}{" "*ceil(n)}'
        else:
            n -= 2
            line = f'{pad*floor(n)}  {text}  {pad*ceil(n)}'
        return ( f'\n{line}\n' if newline else line )

    def head(self, text):
        hr = self.hr()
        line = f'{hr}\n{self.center(text)}\n{hr}'
        return f'\n{line}\n'

    def green_arrow(self, text1, text2):
        print(f"{text1} \x1b[92m=>\x1b[0m {text2}")

    def object(self, obj):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(obj)


#-- SimpleProc ------------------------------------------------------------------#

import shlex
import subprocess

class SimpleProc:
    '''
    Blocking process caller.
    See <https://docs.python.org/3/library/subprocess.html> for details.
    '''

    __version__ = '0.1'

    @classmethod
    def run(cls, cmd, check=False):
        if isinstance(cmd,str): cmd = shlex.split(cmd)
        if check:
            result = subprocess.run(cmd,capture_output=True,check=True)
            return result.stdout.decode('utf-8')
        else:
            result = subprocess.run(cmd,capture_output=True)
            return (
                result.returncode,
                result.stdout.decode('utf-8'),
                result.stderr.decode('utf-8')
            )

    @classmethod
    def stream(cls, cmd, check=False):
        if isinstance(cmd,str): cmd = shlex.split(cmd)
        with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as process:
            if check:
                while True:
                    output = process.stdout.readline().decode().strip()
                    rc = process.poll()
                    if output == '' and rc is not None:
                        break
                    if output:
                        yield output
                if rc != 0:
                    err = subprocess.CalledProcessError(returncode=rc,cmd=cmd)
                    err.stdout = process.stdout.read()
                    err.stderr = process.stderr.read()
                    raise err
            else:
                while True:
                    output = process.stdout.readline().decode().strip()
                    rc = process.poll()
                    if output == '' and rc is not None:
                        break
                    if output:
                        yield (rc,output)
                err = process.stderr.read().decode()
                yield (rc,err)

#-- Local Helpers ---------------------------------------------------------------------------#


def load_toml_config(filepath, clean=True):
    with open(filepath,'r') as f:
        obj = toml.load(f)

    for src in obj['sources']:
        if 'sources__ARR' in src:
            lst = []
            for l in src['sources__ARR'].splitlines():
                l = l.strip()
                if l != '' and not l.startswith('#'):
                    lst.append(l)
            src['sources'] = lst
            if clean:
                del src['sources__ARR']
    return obj

@dataclass
class ChunkSource:
    name: str
    dest: str
    strategy: str = ''
    sources: List = field(default_factory=[])

#-- Main --------------------------------------------------------------------------------------#

def main():
    parser = argparse.ArgumentParser(description='A tool to backup home directories.')
    subparsers = parser.add_subparsers(help='sub-command help',dest='main_command')
    # Version
    p = subparsers.add_parser('version', help='Show version info')
    # List
    p = subparsers.add_parser('ls', help='List configurations')
    # Sync
    p = subparsers.add_parser('sync', help='Run synchronization')
    p.add_argument('config_name',help='Configuration name')
    p.add_argument('--full-path',action='store_true',help='Treat config_name as a filepath')
    p.add_argument('-p','--prompt-pause', action='store_true', help="Pause for a prompt on each chunk.")
    p.add_argument('-n','--dry-run', action='store_true')
    p.add_argument('-d','--dest-root', default=None, help="Specify destination path.")
    # Dump
    p = subparsers.add_parser('dump', help='Dump configuration')
    p.add_argument('config_name',help='Configuration name')
    p.add_argument('--full-path',action='store_true',help='Treat config_name as a filepath')
    # Info
    p = subparsers.add_parser('info', help='Print information on a configuration')
    p.add_argument('config_name',help='Configuration name')
    p.add_argument('--full-path',action='store_true',help='Treat config_name as a filepath')
    # process
    args = parser.parse_args()

    # Look for help/version
    if args.main_command is None:
        # parser.print_usage()
        parser.print_help()
        exit()
    if 'version' == args.main_command:
        print('0.3')
        exit()

    # Make helpers
    P = SnackPrinter()
    HOME = Path.home()

    def _load_config(args):
        if not args.full_path:
            config_path = HOME / f'.config/snackpack/{args.config_name}.toml'
        else:
            config_path = Path(args.config_name)
        obj = load_toml_config(config_path)
        return obj

    #-- Run Command -----------------------------------------------------------------------#

    if 'ls' == args.main_command:
        configdir = HOME/'.config/snackpack'
        for f in configdir.iterdir():
            if f.suffix == '.toml':
                P.gray(P.hr(char='-'))
                P.blue(f.stem)
                P.p(f)
                conf = load_toml_config(f)
                P.p(f'title: {conf["title"]}')
                P.p(f'mount: {conf["look_for_dests"][0]["mount"]}')
        P.gray(P.hr(char='-'))

    else:
        # Load the config file
        try:
            CONFIG = _load_config(args)
        except FileNotFoundError:
            P.rb(f'ERROR: could not find config file: {configfile}')
            exit(1)

        # Run the appropriate command
        if 'dump' == args.main_command:
            P.p(json.dumps(CONFIG,indent=4))

        elif 'info' == args.main_command:
            P.p(P.head('Map'))

            P.blue('List all the paths in HOME')
            all_paths = [ f for f in HOME.iterdir() ]
            P.p(all_paths)

            P.blue('List all the paths in config')
            sync_paths = []
            for src in CONFIG['sources']:
                for f in src['sources']:
                    fpath = HOME/f
                    sync_paths.append(fpath)
            P.p(sync_paths)

            P.blue('Skipping path')
            skipping = list( set(all_paths) - set(sync_paths) )
            skipping.sort()
            for f in skipping:
                P.red(f)

            P.blue('Syncing paths')
            total_kb = 0
            for f in sync_paths:
                P.p(f)
                if f.is_dir() or f.is_file():
                    o = SimpleProc.run(f'du -sk {f}',check=True)
                    kb = int(o.replace(str(f),'').strip())
                    P.p(f'{kb}K')
                    total_kb += kb
                else:
                    print('ERROR?')
            P.p(f'Total {total_kb}K , {total_kb/1000}M, {total_kb/1000**2}G')

        elif 'sync' == args.main_command:

            P.p(P.head('Start'))
            execute = not args.dry_run
            errors = []

            # Check it has the relevant type
            if not CONFIG.get('type',None) == 'jbackup.conf.v1':
                P.redbold('ERROR: The loaded toml source file does not look correct! Exiting.')
                exit(1)

            P.p(P.head('Finding the destination'))

            # Setup our base paths
            DEST_ROOT = None
            if args.dest_root is not None:
                DEST_ROOT = Path(args.dest_root)
                if not DEST_ROOT.is_dir():
                    P.redbold(f'ERROR: The destination directory {DEST_ROOT} does not exsist. Exiting.')
                    exit(1)
            else:
                for dest in CONFIG.get('look_for_dests',[]):
                    if dest.get('type','') == 'mount':
                        mount = Path(dest.get('mount'))
                        path = Path(dest.get('path'))
                        P.gray(f'Looking for mount {mount}...')

                        if execute:
                            if mount.is_mount():
                                P.blue(f'Found mount {mount} and will use as destination.')
                                DEST_ROOT = mount / path
                                if not DEST_ROOT.is_dir():
                                    P.p()
                                    P.p(
                                        f'The path {path} does exist on {mount}. '
                                        'Should we make it?'
                                    )
                                    resp = input("(y/n): ")
                                    if resp == 'y':
                                        DEST_ROOT.mkdir(parents=True,exist_ok=True)
                                        P.green('created.')
                                    else:
                                        P.redbold(f'[bold red]Exiting.')
                                        exit(1)
                                break
                            else:
                                P.gray('... not found')
                        else:
                            DEST_ROOT = mount / path
                if DEST_ROOT is None:
                    P.redbold('ERROR: None of the default destination directories could be found. Exiting.')
                    exit(1)

            # Go over each source chunk
            for chunk_dict in CONFIG['sources']:
                # Load the chunk
                chunk = ChunkSource(**chunk_dict)
                P.p(P.center(f'Syncing {chunk.name}',pad='-',newline=True))

                # Make the base destination
                base_dest = DEST_ROOT/chunk.dest
                if execute:
                    base_dest.mkdir(parents=True,exist_ok=True)

                # Sync the sources
                for f in chunk.sources:
                    src = HOME/f
                    dest = base_dest/f

                    P.blue(f)
                    P.green_arrow(src,dest)

                    if args.prompt_pause and input("continue? (y/n): ") != 'y':
                        P.redbold('Exiting.')
                        exit(1)

                    if src.is_dir():
                        rsync_cmd = f'rsync -av --delete {src}/. {dest}/.'
                        if execute:
                            dest.mkdir(parents=True,exist_ok=True)
                            try:
                                for line in SimpleProc.stream(rsync_cmd,check=True):
                                    P.cyan(f'    {line}')
                            except subprocess.CalledProcessError as e:
                                P.redbold('Error rsyncing:')
                                P.redbold(e.stdout.decode())
                                P.redbold(e.stderr.decode())
                        else:
                            P.gray(rsync_cmd)

                    elif src.is_file():
                        if execute:
                            shutil.copy2(src,dest)
                        else:
                           P.gray(f'copy2 {src} {dest}')
                    else:
                        errors.append(dict(
                            src = src, dest = dest,
                            msg = 'Error: Source is neither source nor directory'
                        ))
                        P.red('Error: Source is neither source nor directory. Skipping.')

                    P.p()

            if len(errors) > 0:
                P.redbold(P.head('Errors'))
                P.red('The following errors were encountered:')
                P.object(errors)

            P.p(P.head('End'))


if __name__ == '__main__':
    main()


