#!/bin/sh
# Checkout from GIT_DIR (--bare) into GIT_WORK_TREE
GIT_DIR=/var/cache/git/repositories/$2 GIT_WORK_TREE=$1 git checkout -f
