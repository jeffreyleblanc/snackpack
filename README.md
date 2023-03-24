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

See the `example.toml` in the root of this repository.


