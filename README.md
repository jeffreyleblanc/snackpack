# Snackpack

Snackpack is a tool for making backups to USB drives written in Python.
It uses a list of paths in your home directory to be synced, and then uses rsync/cp.

## Installation

```sh
# Install as /usr/local/bin/snackpack
$ sudo ./_install.sh

# Uninstall
$ sudo ./_uninstall.sh
```

## Configuration

Configs should be placed in `~/.config/snackpack/`. An example is below.

The easiest way to make one is to run:

```sh
$ ( cd $HOME && ls -1 && ls -d1 .!(|.) )
# --snip--
# Documents
# Downloads
# --snip--
# .bash_aliases
# --snip--
```

Which will output all your home directory with dotfile last.
You can then break this up and comment out files/paths you don't want to sync.


## Example Config File

```toml
# Test Toml file

type = "jbackup.conf.v1"
title = "Basic Backup"

[[look_for_dests]]
type = "mount"
mount = "/media/jim/my-backup"
path = "home"

[[sources]]
name = "Main Directories"
dest = ""
sources__ARR = """
admin
archive
code
# library
# mock-server
sandbox
"""

[[sources]]
name = "Default Directories"
dest = ""
sources__ARR = """
Desktop
Documents
Downloads
Yaks
Pictures
"""

[[sources]]
name = "Dot Files"
dest = "dot-files"
sources__ARR = """
.bash_aliases
# .bash_history
# .bash_logout
.bashrc
# .bashrc~
.bashrc.d
# .cache
# .config
# .cups
.emacs.d
.gitconfig
# .gnome
.gnupg
# .gphoto
# .lesshst
# .local
# .mozilla
.pki
.profile
# .python_history
# .sane
.sqlite_history
.ssh
# .sudo_as_admin_successful
.tmux.conf
.tmux.conf.d
"""
```