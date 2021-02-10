#!/bin/bash
volume=$1
echo "$volume"
diskutil info "$volume" | grep 'Volume UUID'
