#!/bin/bash

rm -rf LeetCode
git clone https://github.com/dennislx/algo-practice.git LeetCode
cp .env LeetCode
cd LeetCode
git clone -b mkdocs --single-branch https://github.com/dennislx/algo-practice.git mkdocs
git clone -b scripts --single-branch https://github.com/dennislx/algo-practice.git scripts

python3 scripts/readme_writer_main.py
COOKIE=$(grep LEETCODE_SESSION .env | xargs)
LEETCODE_SESSION="$COOKIE" python3 scripts/mkdocs_writer_main.py --mock

cp README.md mkdocs/docs/index.md
cp STYLEGUIDE.md mkdocs/docs/styleguide.md

cd mkdocs
mkdocs serve -a localhost:8082