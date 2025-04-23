#!/usr/bin/env sh

mkdir -p ./lib

if [ ! -d "./lib/pyopnsense" ]; then
	git clone --branch firewallendpoints https://github.com/PseudoResonance/pyopnsense.git ./lib/pyopnsense
fi

docker build --build-context root=./ ./docker/ $@
