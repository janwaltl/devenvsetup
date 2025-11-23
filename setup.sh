#!/usr/bin/env bash
# Must be run as the user for which the setup is being done.
# Will prompt for sudo password though

set -e

# Use a temp folder for this setup
TMPDIR=/tmp/setup-dir
SSH_KEY="$HOME/.ssh/devenvsetup_key"

## Pretty printing
COL='\033[0;36m'
NCOL='\033[0m'
DOTFILES_DIR=$REAL_HOME/.dotfiles
VENV="$HOME/.venv"

function print_progress(){
	echo -e "${COL}<====" "$@" "====>${NCOL}"
}

function wait_confirm(){
# $1 Wait prompt string
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
	sudo rm -rf "$TMPDIR"
}

trap cleanup EXIT

# Move to a temporary folder
sudo mkdir -p $TMPDIR
sudo chmod a+rwx $TMPDIR
cp -r ./* ${TMPDIR}/
pushd $TMPDIR

print_progress "Setting up SSH keys"
if [ ! -f "$SSH_KEY" ]; then
	print_progress "Generating primary key at ${SSH_KEY}"
	ssh-keygen -t ed25519 -f "$SSH_KEY"
	cat "$SSH_KEY.pub"
	print_progress "Setting it as default for Github"
	cat >> ~/.ssh/config <<-EOF
	Host github.com
	    HostName github.com
	    PreferredAuthentications publickey
	    IdentityFile $SSH_KEY
	EOF
	wait_confirm "Please add $SSH_KEY to your GitHub account"
else
	print_progress "Primary key exists, skipping setup."
fi

print_progress "Installing Ansible"
sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv

[ -d $VENV ] || python3 -m venv $VENV
source $VENV/bin/activate
pip3 install ansible

print_progress "Setting up dotfiles"
ansible-playbook dotfiles.yml
source ~/.bashrc
source $VENV/bin/activate

print_progress "Installing core packages"
ansible-playbook core.yml -kK



print_progress "Installing VIM"
bash install_neovim.sh

print_progress "Installing Tmux"
bash install_tmux.sh

