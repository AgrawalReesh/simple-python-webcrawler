List of files (in alphabetical order):
1. crawler.py - The main crawler script. Run this by using ==> $python crawler.py
2. explain.txt - Contains explanation of the program
3. pygoogle.py - google script that provides “top” search results on a user query
4. pygoogle.pyc - byte code of pygoogle script
5. setup.py - pygoogle uses this setup script
6. readme.txt

How to run?:
make sure you are connected to the internet
Run the crawler.py by using ==> $python crawler.py

Other files/folders:

* Two empty folders “files” and “logs” 

* “files” folder stores all the crawled content by downloading every page in a separate file which is named with following convention ==> file[number].txt

* “logs” folder will store the log file ==> log_main.txt. Following are the fields of every row ==> Sr. no; url; level (distance from root); time crawled at; size of file; response code; page score. The log_main.txt file also stores a summary at the end of the file. 

* examples folder contains 4 outputs as described above

Output:
1.  /files/file[number].txt
2.  /logs/log_main.txt
