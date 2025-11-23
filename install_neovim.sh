#!/usr/bin/env bash

set -e

# Neovim prereqs
sudo apt-get install -y liblua5.1-dev luajit libluajit-5.1-dev libperl-dev libncurses5-dev ruby-dev


CLONE_DIR="${HOME}/nvim/"

if [ ! -d "${CLONE_DIR}" ];then
	git clone --depth 1 https://github.com/neovim/neovim "${CLONE_DIR}"
fi

cd "${CLONE_DIR}"
git pull
# Build
make CMAKE_BUILD_TYPE=RelWithDebInfo "CMAKE_INSTALL_PREFIX=${HOME}/.local/"

# Install
make install
