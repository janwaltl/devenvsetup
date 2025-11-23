#!/usr/bin/env bash


sudo apt-get install -y libevent-dev ncurses-dev build-essential bison pkg-config automake

CLONE_DIR=/tmp/tmux.build
if [ ! -d ${CLONE_DIR} ];then
	git clone --depth 1 git@github.com:tmux/tmux.git ${CLONE_DIR}
fi

cd ${CLONE_DIR}

sh autogen.sh
./configure --prefix=$HOME/.local
make && sudo make install

TPM_DIR=~/.tmux/plugins/tpm
if [ ! -d ${TPM_DIR} ];then
	git clone https://github.com/tmux-plugins/tpm ${TPM_DIR}
fi
