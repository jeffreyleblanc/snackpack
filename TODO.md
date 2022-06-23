
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
