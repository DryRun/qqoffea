#!/bin/bash
echo "Tunneling to ${1}, port ${2}"
ssh -v -N -L localhost:${2}:localhost:${2} $(whoami)@lxplus${1}.cern.ch
