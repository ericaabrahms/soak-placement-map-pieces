#!/usr/bin/env bash
poetry run python3 main.py pieces
poetry run python3 main.py art
poetry run python3 main.py camps

for file in $PWD/sign_images_before/*.jpg; do
    echo "Checking file: $file"
    result=$(compare -metric AE "${file}" "${file/_before/}" /tmp/sign-diff.jpg 2>&1);
    if [ "${result}" != '0' ]; then
        echo "${result} incorrect pixels in ${file}";
        exit 1
    fi;
done;

for file in $PWD/images_before/*.jpg; do
    echo "Checking file: $file"
    result=$(compare -metric AE "${file}" "${file/_before/}" /tmp/camp-art-diff.jpg 2>&1);
    if [ "${result}" != '0' ]; then
        echo "${result} incorrect pixels in ${file}";
        exit 1
    fi;
done;