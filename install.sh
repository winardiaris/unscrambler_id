#!/usr/bin/env bash
UNSCRAMBLER_DIR=$HOME/.unscrambler_id

if ! [ -x "$(command -v git)" ]; then
    echo 'Error: git is not installed.' >&2
    exit 1
fi

if ! [ -x "$(command -v python)" ]; then
    echo 'Error: python is not installed.' >&2
    exit 1
fi

if ! [ -x "$(command -v pip)" ]; then
    echo 'Error: pip is not installed.' >&2
    exit 1
fi

git clone --recurse-submodules https://github.com/winardiaris/unscrambler_id.git "$UNSCRAMBLER_DIR"
git config --global --add safe.directory "$UNSCRAMBLER_DIR"
cd "$UNSCRAMBLER_DIR" || exit
pip install -r requirement.txt

if [ "$SHELL" == '/usr/bin/zsh' ]; then
    echo "UNSCRAMBLER_DIR=$HOME/.unscrambler_id" >>~/.zshrc
    echo "export PATH=\"\$UNSCRAMBLER_DIR:\$PATH\"" >>~/.zshrc
elif [ "$SHELL" == '/bin/bash' ]; then
    echo "UNSCRAMBLER_DIR=$HOME/.unscrambler_id" >>~/.bashrc
    echo "export PATH=\"\$UNSCRAMBLER_DIR:\$PATH\"" >>~/.bashrc
else
    echo "Please add ${UNSCRAMBLER_DIR} to your PATH"
fi
