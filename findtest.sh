#!/bin/bash
finditem=$1
shift
./indexer.py  -f $finditem -d '/Users/johnny/.indexer.sqlite' -n '%' --query --dryrun $@
#./indexer.py  -f 'b56021ae96a2e41957a3e808394bd416' -d '/Users/johnny/.indexer.sqlite' -n '%' --hash
#./indexer.py  -f $1 -d '/Users/johnny/.indexer.sqlite' -n '%' --query --searchpath
