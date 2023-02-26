#!/bin/sh

for d in `ls -d */`
do 
    echo $d,`find $d -type f |wc -l`
done
