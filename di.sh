#!/bin/bash
volume=$1
diskutil info $volume | grep 'Volume UUID'
shift
echo $@

#echo "Hello, world $v!"
#echo $v

#v = 'hello world'
#shift
#echo $v
#echo $@
