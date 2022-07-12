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
from functools import partial
from rich.console import Console

class RichPrinter:

    __version__ = '0.1.snackpack'

    COLOR_MAP = dict(
        p = '',
        r = 'red',
        g = 'green',
        b = 'dodger_blue2',
        y = 'yellow1',
        c = 'cyan',
        m = 'magenta',
        k = 'grey30'
    )

    def __init__(self):
        self.console = Console(highlight=False)
        self._cached_meth = dict()

    def __getattr__(self, k):
        if k in self._cached_meth: return self._cached_meth[k]
        bold = ' bold' if len(k) > 1 else ''
        color = self.COLOR_MAP[k[0]]
        meth = partial(self._p, s=f'{color}{bold}')
        self._cached_meth[k] = meth
        return meth

    def _p(self, *args, **kwargs):
        justify = kwargs.get('j',None)
        indent = kwargs.get('i',None)
        padding = kwargs.get('p',False)
        style = kwargs.get('s',None)
        text = args[0] if len(args)==1 else ''
        if indent is not None:
            text = textwrap.indent(text, prefix=' '*indent)
        if padding: self.console.print()
        self.console.print(text,justify=justify,style=style)
        if padding: self.console.print()

    def header(self, text, **kwargs):
        p = kwargs.pop('p',True)
        if p: self.p()
        meth = getattr(self,kwargs.get('s','p'))
        line = '='*self.console.size.width
        meth(line)
        meth(text,j=kwargs.get('j','center'))
        meth(line)
        if p: self.p()

    def hr(self, **kwargs):
        padding = kwargs.get('p',True)
        call_style = kwargs.get('s','p')
        tcol = self.console.size.width
        getattr(self,call_style)('-'*tcol,p=padding)

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
    parser = argparse.ArgumentParser(description="A tool to backup home directories")
    parser.add_argument('-d','--dest-root', default=None, help="Specify destination path.")
    parser.add_argument('-c','--config', default=None, help="Specify path to config file to use")
    parser.add_argument('-p','--prompt-pause', action='store_true', help="Pause for a prompt on each chunk.")
    parser.add_argument('-n','--dry-run', action='store_true')
    parser.add_argument('--list-configs', action='store_true')
    parser.add_argument('--examine', action='store_true')
    parser.add_argument('--map', action='store_true')
    parser.add_argument('--version', action='store_true')
    args = parser.parse_args()

    if(args.version):
        print('0.2')
        exit()

    P = RichPrinter()
    HOME = Path.home()

    if args.list_configs:
        configdir = HOME/'.config/snackpack'
        for f in configdir.iterdir():
            if f.suffix == '.toml':
                P.rule()
                P.b(f)
                obj = load_toml_config(f)
                P.p(f'title: {obj["title"]}')
                P.p(f'mount: {obj["look_for_dests"][0]["mount"]}')
        P.rule()

    elif args.examine:
        assert args.config is not None
        try:
            configfile = Path(args.config)
            obj = load_toml_config(configfile)
            P.p(json.dumps(obj,indent=4))
        except FileNotFoundError:
            P.rb(f'ERROR: could not find config file: {configfile}')
            exit(1)

    elif args.map:
        assert args.config is not None
        try:
            configfile = Path(args.config)
            obj = load_toml_config(configfile)
        except FileNotFoundError:
            P.rb(f'ERROR: could not find config file: {configfile}')
            exit(1)

        P.header('Map')

        P.b('List all the paths in HOME')
        all_paths = [ f for f in HOME.iterdir() ]
        print(all_paths)

        P.b('List all the paths in config')
        sync_paths = []
        for src in obj['sources']:
            for f in src['sources']:
                fpath = HOME/f
                sync_paths.append(fpath)
        print(sync_paths)

        P.b('Skipping path')
        skipping = list( set(all_paths) - set(sync_paths) )
        skipping.sort()
        for f in skipping:
            P.r(f)

        P.b('Syncing paths')
        total_kb = 0
        for f in sync_paths:
            P.p(f)
            if f.is_dir() or f.is_file():
                o = SimpleProc.run(f'du -sk {f}',check=True)
                kb = int(o.replace(str(f),'').strip())
                print(f'{kb}K')
                total_kb += kb
            else:
                print('ERROR?')
        print(f'Total {total_kb}K , {total_kb/1000}M, {total_kb/1000**2}G')

    else:

        P.header('Start')

        execute = not args.dry_run
        errors = []

        P.header('Finding the config')

        # load the toml source
        configfile = None
        if args.config is not None:
            try:
                configfile = Path(args.config)
            except FileNotFoundError:
                P.rb(f'ERROR: could not find config file: {configfile}')
                exit(1)
        else:
            configdir = HOME/'.config/snackpack'
            P.b(f'Looking for a default config in {configdir}...')
            if not configdir.is_dir():
                P.rb(f'ERROR: No default config directory found at {configdir}')
                exit(1)
            for f in configdir.iterdir():
                configfile = f
                P.b(f'Found and using {f}')
                break

        P.header(f'Loading the config');

        obj = load_toml_config(configfile)

        # Check it has the relevant type
        if not obj.get('type',None) == 'jbackup.conf.v1':
            P.rb('ERROR: The loaded toml source file does not look correct! Exiting.')
            exit(1)

        P.header('Finding the destination');

        # Setup our base paths
        DEST_ROOT = None
        if args.dest_root is not None:
            DEST_ROOT = Path(args.dest_root)
            if not DEST_ROOT.is_dir():
                P.rb(f'ERROR: The destination directory {DEST_ROOT} does not exsist. Exiting.')
                exit(1)
        else:
            for dest in obj.get('look_for_dests',[]):
                if dest.get('type','') == 'mount':
                    mount = Path(dest.get('mount'))
                    path = Path(dest.get('path'))
                    P.k(f'Looking for mount {mount}...')

                    if mount.is_mount():
                        P.b(f'Found mount {mount} and will use as destination.')
                        DEST_ROOT = mount / path
                        if not DEST_ROOT.is_dir():
                            P.console.print()
                            P.console.print(
                                f'The path [bright_cyan]{path}[/bright_cyan] does exist on [bright_cyan]{mount}[/bright_cyan]. '
                                'Should we make it?'
                            )
                            resp = P.console.input("(y/n): ")
                            if resp == 'y':
                                DEST_ROOT.mkdir(parents=True,exist_ok=True)
                                P.g('created.')
                            else:
                                P.rb(f'[bold red]Exiting.')
                                exit(1)
                        break
                    else:
                        P.k('... not found')
            if DEST_ROOT is None:
                P.rb('ERROR: None of the default destination directories could be found. Exiting.')
                exit(1)

        # Go over each source chunk
        for chunk_dict in obj['sources']:
            # Load the chunk
            chunk = ChunkSource(**chunk_dict)
            P.console.rule(f'[blue]Syncing[/blue] [bold]{chunk.name}')

            # Make the base destination
            base_dest = DEST_ROOT/chunk.dest
            base_dest.mkdir(parents=True,exist_ok=True)

            # Sync the sources
            for f in chunk.sources:
                src = HOME/f
                dest = base_dest/f

                P.b(f)
                P.p(f'{src} [green]=>[/green] {dest}')

                if args.prompt_pause and console.input("continue? (y/n): ") != 'y':
                    P.rb('Exiting.')
                    exit(1)

                if src.is_dir():
                    rsync_cmd = f'rsync -av --delete {src}/. {dest}/.'
                    if execute:
                        dest.mkdir(parents=True,exist_ok=True)
                        try:
                            for line in SimpleProc.stream(rsync_cmd,check=True):
                                P.c(f'    {line}')
                        except subprocess.CalledProcessError as e:
                            P.rb('Error rsyncing:')
                            P.rb(e.stdout.decode())
                            P.rb(e.stderr.decode())
                    else:
                        P.k(rsync_cmd)

                elif src.is_file():
                    if execute:
                        shutil.copy2(src,dest)
                    else:
                       P.k(f'copy2 {src} {dest}')
                else:
                    errors.append(dict(
                        src = src, dest = dest,
                        msg = 'Error: Source is neither source nor directory'
                    ))
                    P.r('Error: Source is neither source nor directory. Skipping.')

                P.p()

        if len(errors) > 0:
            P.header('Errors',s='rb')
            P.r('The following errors were encountered:')
            P.console.print(errors,highlight=True)

        P.header('End')


if __name__ == '__main__':
    main()


