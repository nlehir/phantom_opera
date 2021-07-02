#!/bin/bash

i="0"

nbRuns=$1

while [ $i -lt $nbRuns ]
do
  py ./random_fantom.py&
  i=$[$i+1]
done

i="0"
while [ $i -lt $nbRuns ]
do
  py ./random_inspector.py&
  i=$[$i+1]
done
