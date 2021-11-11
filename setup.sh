#!/usr/bin/env bash

set -e
SSH_KEY="$HOME/.ssh/primary_key"

COL='\033[0;36m'
NCOL='\033[0m'
DOTFILES_DIR=$HOME/.dotfiles

TMPDIR=/tmp/setup-dir

function print_progress(){
	echo -e "${COL}<====" "$@" "====>${NCOL}"
}

function wait_confirm(){
# $1 Wait prompt
while true; do
	read -p "$(echo -e ${COL}$1${NCOL}) (y/n)" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit 1;;
        * ) echo "Please answer yes or no.";;
    esac
done
}

function cleanup(){
	rm -rf "$TMPDIR"
}

trap cleanup EXIT

mkdir $TMPDIR
pushd $TMPDIR

print_progress "Upgrading packages"
sudo apt update
sudo apt upgrade
sudo apt autoremove -y

print_progress "Installing basic tools"
sudo apt install -y  build-essential bear git gawk python3-dev python3-pip python-dev

print_progress "Installing LLVM toolchain"
sudo apt install -y  llvm-11 clang-format-11 clang-tools-11 clang-tidy clang-11 clangd-11
if [ ! -f "/usr/bin/clangd" ]; then
	sudo ln -s $(which clangd-11) /usr/bin/clangd
fi

print_progress "Installing GCC toolchain"
sudo apt install -y gcc-10-multilib

sudo apt autoremove -y


if [ ! -f "$SSH_KEY" ];then
	print_progress "Generating primary key"
	ssh-keygen -t ed25519 -f "$SSH_KEY"
	cat "$SSH_KEY.pub"
	print_progress "Setting it as default for Github"
	cat >> ~/.ssh/config <<-EOF
	Host github.com
	    HostName github.com
	    PreferredAuthentications publickey
	    IdentityFile $SSH_KEY
	EOF
else
	print_progress "Primary key exists, skipping setup."
fi


git config --global user.name "Jan Waltl"
git config --global user.email "waltl.jan@gmail.com"
git config --global pull.rebase true


wait_confirm "Please add the key to Github, done?"


if [ ! -d "$DOTFILES_DIR" ]; then
	print_progress "Setting up dotfiles"
	git clone git@github.com:janwaltl/dotfiles.git $DOTFILES_DIR
	ln -s $DOTFILES_DIR/.vimrc $HOME/.vimrc
	ln -s $DOTFILES_DIR/.tmux.conf $HOME/.tmux.conf
	ln -s $DOTFILES_DIR/.clang-format $HOME/.clang-format
else
	print_progress "Dot files present, skipping"
fi

print_progress "Installing VIM"

# Vim,neovim dependencies
sudo apt-get install liblua5.1-dev luajit libluajit-5.1 libperl-dev libncurses5-dev ruby-dev

# Clean and prepare folders
sudo mkdir -p /usr/include/lua5.1/include

# Download it and compile
#pushd /usr/local/src/
#git clone https://github.com/vim/vim
#pushd vim/src
#make distclean

#./configure --with-features=huge \
#            --enable-rubyinterp \
#            --with-ruby-command=$(which ruby) \
#            --enable-largefile \
#            --disable-netbeans \
#            --enable-python3interp=yes \
#            --with-python3-config-dir=$(python3-config --config-dir) \
#            --enable-perlinterp \
#            --enable-luainterp \
#            --with-luajit \
#            --enable-fail-if-missing \
#            --with-lua-prefix=/usr/include/lua5.1 \
#            --enable-cscope

make
sudo make -j8 install

popd

if ! command -v nvim &> /dev/null
then
	print_progress "Installing Neovim"
	wget https://github.com/neovim/neovim/releases/download/v0.5.1/nvim-linux64.tar.gz
	tar -xzf nvim-linux64.tar.gz

	cp -r nvim-linux64/* $HOME/.local/
	ln -s $HOME/.local/bin/nvim $HOME/.local/bin/vim

else
	print_progress "Neovim already present"
fi

print_progress "Installing Coc extensions"
nvim +'CocInstall -sync coc-clangd' +qall
nvim +'CocInstall -sync coc-snippets' +qall
nvim +'CocInstall -sync coc-pyright' +qall

print_progress "Python packages for Neovim"
python3 -m pip install --user --upgrade pynvim doq



##### TMUX

sudo apt install tmux -y
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm


#### Python
