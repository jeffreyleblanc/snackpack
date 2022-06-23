#! /usr/bin/env bash

set -e

echo "Ensuring the holder exists"

mkdir -p $HOME/.config/snackpack

echo "Copy in the config files"

cp configs/thinkpad-basic.yaml $HOME/.config/snackpack/

echo "...Finished."