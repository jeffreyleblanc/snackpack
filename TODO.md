# TODO

* [ ] make ls also list mounted items and tag if one of the configs has a mounted item
* [x] enable a config file to have multiple mounts it can use
* [ ] make a `build-config` command that will generate a config file scaffold

* [ ] make sure comes up with total size of backup
    * [ ] on host
    * [ ] look at size diff with target storage as well

* [ ] info should sort what syncing by alphabet and use human readable size info
* [ ] we need some way to check state of a target drive better
    * [ ] especially if it has root directories no longer tracked

---

Low priorities but:

* [ ] make a log in .config/snackpack/backup of all the backups, and flags with timestamp
    * [ ] Also log on the target drive somehow
* [ ] maybe try --progress and/or --partial on the rsync? however these might be updating specific lines...
* [ ] test interruption

More likely we should think about encrypted remote backups over ssh?

