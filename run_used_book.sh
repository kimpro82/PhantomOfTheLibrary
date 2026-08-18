#!/bin/bash

cd Aladin

python3 -m pip install --upgrade pip
pip install -r requirements.txt
python3 used_book_2.1.py 20260818.yaml
