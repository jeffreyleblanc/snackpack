#! /usr/bin/env bash

if [ $(id -u) -ne 0 ]; then
    echo 'You must be root to run this command.'
    exit 1
fi

echo "Removing programs from /usr/local/bin..."

rm -f /usr/local/bin/snackpack

echo "Any config files in ~/.config/snackpack are left there"

echo "...Finished."
