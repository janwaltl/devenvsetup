#!/usr/bin/env bash
# Must be run as the user for which the setup is being done.
# Will prompt for sudo password though

set -e

# Use a temp folder for this setup
TMPDIR=/tmp/setup-dir
SSH_KEY="$HOME/.ssh/primary_key"

## Pretty printing
COL='\033[0;36m'
NCOL='\033[0m'
DOTFILES_DIR=$REAL_HOME/.dotfiles

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

print_progress "Installing Ansible"
sudo apt-get install python3-dev python3-pip python3-virtualenv
pip3 install ansible ansible-base --break-system-packages

ansible-galaxy collection install community.general

print_progress "Installing core packages"
ansible-playbook core.yml -kK

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
else
	print_progress "Primary key exists, skipping setup."
fi

print_progress "Setting up dotfiles"
ansible-playbook dotfiles.yml

print_progress "Installing VIM"
bash install_neovim.sh

print_progress "Installing Tmux"
bash install_tmux.sh

