#!/bin/bash

while true;
do
    python coding_challenge.py
    if [ $? -eq -1 ]
    then
	python coding_challenge.py
    fi
done
