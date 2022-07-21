
## TODO

1) Gather elsewhere all the argparse examples we have
    * esp. basic subcommands
    * see <https://docs.python.org/3/library/argparse.html#sub-commands>
2) Implement subcommands for snackpack
2a) Confirm `-n` and `-p` commands
3) Implement ability to use shortcut config name
4) Evaluate and then remove `-d` option
5) Gather elsewhere all our stdlib terminal styling code
6) Remove `rich` dependency
    * see jknowledge/scaffolds/python-terminal/printer-1.py
7) Cleanup the current `--map` output so it is more useful


## 20220720 Review

### Reviewing our flags

Looking at the current help

```sh
A tool to backup home directories

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_ROOT, --dest-root DEST_ROOT
                        Specify destination path.
  -c CONFIG, --config CONFIG
                        Specify path to config file to use
  -p, --prompt-pause    Pause for a prompt on each chunk.
  -n, --dry-run
  --list-configs
  --examine
  --map
  --version
```

So what do we actually do:

```sh
## Get the version
snackpack --version

## List Configs
snackpack --list-configs
#=> list a shortcut name?

## Run a config
snackpack -c ~/.config/snackpack/thinkpad-basic.toml
#=> split into
# 1) be able to do a shortcut to file name
snackpack -c/--config think-basic
# 2) Full config path
snackpack --config-path FULLPATH

## CONFIRM
-n works
-p works

## REMOVE
-d ... why do we need this at this point? seems confusing

## --examine ... does?
It is used to dump a config file, ala:
snackpack -c ~/.config/snackpack/thinkpad-basic.toml --examine

## --map is used as such:
snackpack -c ~/.config/snackpack/thinkpad-basic.toml --map
And dumps info on what is tracked, what is not, and sizes
Needs to be cleaned up
```

Likely we should do sub commands like:

```sh
snackpack --version

snackpack ls            # list commands
snackpack run $CONFIG   [-n/-p] # current default run command
snackpack dump $CONFIG  # current --examine flag
snackpack map $CONFIG   # current --map flag, better name?



## OLDER

snackpack has been great, these two features will really be worth it

updates to the actual sync:

1. get a list of mounted media
  * if none, exit with error
2. then iterate over the configs to find one config file
  * or exit with error


* [ ] Make snackpack match whatever source configs there are to the device mounted, and if one match, can run
* [ ] Make a --map command that will
  * [ ] load a config (via -c )
  * [ ] look within $HOME at what is and is not being tracked
  * [ ] look at total size for all tracked and untracked things

---

* [x] test (and handle) what happens when a source is not there
  * [x] gather any errors and present at the end
* [x] argparse option to specify full dest path
* [x] allow the .yaml to specify default paths
* [x] enforce checks on these default paths
* [x] test the behavior of sh.rsync
  * [x] basic output capture... can we print in realtime
  * [ ] errors if source or dest not there
  * [ ] determine what to do with errors... maybe just add to report
* [x] hook it up and try it out

* [ ] make a log in .jlocal/backup of all the backups, and flags with timestamp


maybe try --progress and/or --partial on the rsync? however these might be updating specific lines...

---

Abandon the shell script, too complicated

Install python-rich

Do the python script as args and paths will be much easier to deal with


---


WHAT IF: this actually was designed to generate a shell script instead of just a python script?
Issue here, is how to stream output from a sub command to the python stdout?

* clean up double rsync for loop
  * but probably use the second one
* no need to use aproc here probably, just normal blocking as I'm not sure rsync in paralell is worth anything

* test interruption


* break apart main into a class, and just pass in the src/dst listings
* add more src/dst (Desktop, Pictures, Downloads, etc)
