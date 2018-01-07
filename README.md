# Go-Capture
This is a Python 3.X script that interacts with Google's Activity timeline to capture and extract the activity cards to a spreadsheet. Be aware that this script can break and will require updates with any changes to Google's Activity timeline HTML objects or URL.
## Usage
This script takes up to five arguments: the username, password, the output file path for the resulting CSV, the number of times to scroll to the bottom of the page, and the number of seconds to wait between each scroll. Be aware that when supplying the password argument, you may need to wrap it in double quotes as some characters caused issues.
~~~
python go_capture.py -h
usage: go_capture.py [-h] -u USERNAME -p PASSWORD -c COUNT -o OUTPUT
                     [-s SECONDS]

Capture Google My Activity..

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Google account user: username@gmail.com
  -p PASSWORD, --password PASSWORD
                        Google account password
  -c COUNT, --count COUNT
                        Number of times to scroll to the end of the page
  -o OUTPUT, --output OUTPUT
                        Output CSV
  -s SECONDS, --seconds SECONDS
                        Number of seconds to wait before pressing END (default
                        1 second)
~~~
