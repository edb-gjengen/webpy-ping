#!/bin/sh
# Does the following:
# - Clone from bare dir into TMP_DIR
# - Clone submodules
# - Delete .git directories
# - Copy to deploy dir

DIR="$( cd "$( dirname "$0" )" && pwd )"
REPO_BARE_GIT_DIR="/var/cache/git/repositories/$2"
DEPLOY_DIR=$1
TMP_DIR="/tmp/git-deploy"
unset GID_DIR
{
    date
    git clone $REPO_BARE_GIT_DIR $TMP_DIR
    cd $TMP_DIR
    if [ -f ".gitmodules" ]; then
        git submodule update --init
        git submodule foreach 'rm -rf .git/'
    fi
    rm -rf .git
    echo "Copying contents of '$TMP_DIR' to '$DEPLOY_DIR'..."
    cp -R $TMP_DIR/* $DEPLOY_DIR
    rm -rf $TMP_DIR
} >> "$DIR/deploy.log"
