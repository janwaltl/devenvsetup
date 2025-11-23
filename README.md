Scripts for setting my debian-based development environment.

I use neovim as my IDE and mainly work with C++, Python, Rust, and some CI/bash/ansible stuff.

Feel free to use anything from here and do not hesitate to ask me if something is not clear or you have trouble with getting it working on your machine.

**Installs:**
 - Python3 including virtualenv,
 - Ansible,
 - LLVM-19 with clang and other goodies,
 - g++-14, gcc-14, bear, compiledb,
 - neovim with plugins,
 - tmux,
 - all my [dotfiles](https://github.com/janwaltl/dotfiles),
 - some other bits.

# Usage
Should work out of the box for Debian Trixie or similar.

0. Please read through the above section, the ansible playbooks, and `setup.sh` to understand what will be downloaded, 
updated **and potentially removed** from your system.
1. Clone to any directory.
2. Run `./setup.sh`, input sudo password when prompted. Do NOT run the script itself as root (with `sudo`), it would install the files to the wrong home directory.

Note that only the non-existent dotfiles are linked, see [dotfiles.yml]() for list of them, delete yours if you want mine to be installed.

**Alternatively**, you can call `ansible-playbook <file.yml>` for each `.yml` here, asumming you installed ansible.

# First run
**Neovim**:
1. Start, Lazy plugin should bootstrap itself and itself all other plugins to version specified in dotfiles.
1. Wait for treesitter and other plugins (see status line, notifications).
1. Restart and run `:Mason`, wait for all tools to be installed.
1. Restart neovim.
**Tmux**:
1. Press `CTRL-A` and (then) `I`, this will download all plugins, wait for a while until the colorscheme changes, there is no progress bar.
1. Restart tmux.

# Keybindings
See [dotfiles](https://github.com/janwaltl/dotfiles)

# LICENSE
Public Domain
