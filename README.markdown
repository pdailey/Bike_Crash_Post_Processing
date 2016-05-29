# How to run the post processing scripts
The post processing scripts take the data from the BBB and Arduino and creates CSV files.

Requirements: Python 3, pip and R

1. Setup the environemnt:
The following packages are used in this script. Install with pip.
`pip install pathlib arrow fuzzywuzzy pandas folium tqdm`

- arrow - offers a sensible, human-friendly approach to creating, manipulating, formatting and converting dates, times, and timestamps.
- pathlib - support for OS-agnostic file system manipulation. Script can run in unix, mac, etc...
- fuzzywuzzy - fuzzy string matching, used to find files even when they don't exactly match.
- pandas - powerful Python data analysis toolkit.
- folium - visualize GPS data on a Leafleft map via Folium. Uses Open Street Map.
- tqdm - provides progress bars.

2. Create a directory to process ride data in.

`mkdir Post_Processing Scripts`
`cd Post_Processing Scripts`
`mkdir Unprocessed_Data`

Place files to be processed into the folder `Unprocessed_Data`.


