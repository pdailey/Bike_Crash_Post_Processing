# How to run the post processing scripts
The post processing scripts take the data from the BBB and Arduino and creates CSV files. If RStudio is installed, the script can also generate plots.

### Requirements
This guide assumes you already have Python 3, pip and R installed. If not, install them.

### Setup the environment:
The following packages are used in this script. Install with pip.
```
pip install pathlib arrow fuzzywuzzy pandas folium tqdm
```

- arrow - offers a sensible, human-friendly approach to creating, manipulating, formatting and converting dates, times, and timestamps.
- pathlib - support for OS-agnostic file system manipulation. Allows script to run on Windows, Unix, Mac, etc...
- fuzzywuzzy - fuzzy string matching, used to find files even when they don't exactly match.
- pandas - powerful Python data analysis toolkit.
- folium - visualize GPS data on a Leafleft map via Folium. Uses Open Street Map.
- tqdm - provides progress bars on the command line.

#### Create a directory to process ride data
```
mkdir Post_Processing Scripts
cd Post_Processing Scripts
mkdir Unprocessed_Data
```

#### Clone the scripts from github


### Add files to be processed
Place files to be processed into the folder `Unprocessed_Data`. These include:
```
calibration.csv
cadence.csv,
front_brake.csv,
rear_brake.csv,
imu.csv,
steering.csv,
wheelspeed.csv
```
If the filenames do not exactly match, the script will identify and use the closest match.

