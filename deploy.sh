#!/bin/bash

echo -e "[ \033[0;33mRUN THIS UNDER VIRTUALENV\033[0m ]"

# rm dists directories
rm -fr seminaires/dist

# rm generated packages folders
rm -fr seminaires/seminaires.egg-info

# generating packages
python3 seminaires/setup.py sdist

echo -e "[ \033[0;33m now installing deployment app via pip\033[0m ]"

# install generated package via 'pip'
pip install --upgrade seminaires/dist/seminaires-1337.tar.gz
