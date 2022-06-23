#! /usr/bin/env bash

if [ $(id -u) -ne 0 ]; then
    echo 'You must be root to run this command.'
    exit 1
fi

echo "Copying programs into /usr/local/bin..."

cp snackpack.py /usr/local/bin/snackpack
chmod 755 /usr/local/bin/snackpack

echo "...Finished."