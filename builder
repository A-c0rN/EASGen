#!/bin/bash

rm -rf dist/
rm -rf EASGen.egg-info/
python3 -m build
python3 -m twine upload dist/*