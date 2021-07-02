#!/bin/bash

ulimit -l unlimited
ulimit -n 10240
ulimit -u 10240

i="0"

nbRuns="10"

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
