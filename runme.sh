diskutil info '/Volumes/Seagate Backup Plus Drive/' | grep 'Volume UUID'
#./indexer.py -h /Volumes/UNTITLED -r /Volumes/UNTITLED -d /Users/johnny/.indexer.sqlite -n jkw -b 32768
./indexer.py --report -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/' -d '/Users/johnny/.indexer.sqlite' -n kenny -b 32768
