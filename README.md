Scripts for setting my debian-based development environment.

I use neovim as my IDE and mainly work with C++, python, and some CI/bash/ansible stuff.

Feel free to use anything from here and do not hesitate to ask me if something is not clear or you have trouble with getting it working on your machine.

Installs:
 - Python3 including virtualenv,
 - Ansible,
 - LLVM-11 with clang and other goodies,
 - g++-10, gcc-10, bear, compiledb,
 - neovim with plugins,
 - tmux,
 - all my [dotfiles](https://github.com/janwaltl/dotfiles),
 - some other bits.

# Usage
Should work out of the box for recent versions of debian-based systems like debian, ubuntu, or mint.

0. Please read through the above section, the ansible playbooks, and `setup.sh` to understand what will be downloaded, updated **and potentially removed** from your system. In particular, common dotfiles are overrriden with my own.
1. Clone to any folder.
2. Run `./setup.sh`, input sudo password when prompted. Do NOT run the script itself as root (with `sudo`), it would install the files to the wrong home directory.

# LICENSE
Public Domain
