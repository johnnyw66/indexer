diskutil info '/Volumes/Seagate Backup Plus Drive/' | grep 'Volume UUID'
#./indexer.py -h /dev/disk1s5 -r . -d sb_util.sqlite -n example_name4
#./indexer.py -h /Volumes/UNTITLED -r /Volumes/UNTITLED -d xxx -n jkw -b 32768
./indexer.py -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/' -d xxx -n kenny -b 32768
