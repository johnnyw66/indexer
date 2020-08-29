diskutil info '/Volumes/MacBookAirTimeMachine/' | grep 'Volume UUID'

#./indexer.py -h /Volumes/UNTITLED -r /Volumes/UNTITLED -d /Users/johnny/.indexer.sqlite -n jkw -b 32768 --scanning
#./indexer.py -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/' -d '/Users/johnny/.indexer.sqlite' -n kenny -b 32768 --scanning
#./indexer.py -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/' -d '/Users/johnny/.indexer.sqlite' -n collie -b 32768 --scanning
#./indexer.py -h '/Volumes/Backup Nov 2012' -r '/Volumes/Backup Nov 2012/' -d '/Users/johnny/.indexer.sqlite' -n paul -b 32768 --scanning
#./indexer.py -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/' -d '/Users/johnny/.indexer.sqlite' -n mike -b 32768 --scanning
#./indexer.py -h '/Volumes/Seagate Backup Plus Drive/' -r '/Volumes/Seagate Backup Plus Drive/SQLITE/' -d '/Users/johnny/.indexer.sqlite' -n mike -b 32768 --scanning
#./indexer.py -h '/Volumes/MacBookAirTimeMachine/' -r '/Volumes/MacBookAirTimeMachine/' -d '/Users/johnny/.indexer.sqlite' -n sue -b 32768 --scanning
./indexer.py -h '/Volumes/Untitled/' -r '/Volumes/Untitled/' -d '/Users/johnny/.indexer.sqlite' -n lizzy -b 32768 --scanning

./indexer.py  -d '/Users/johnny/.indexer.sqlite' --report
#./email.py -m 'Indexing Completed' -t 'johnnyw66@gmail.com' -s 'Indexing Job Complete'
