# How to run the post processing scripts
The post processing scripts take the data from the BBB and Arduino and creates CSV files. If RStudio is installed, the script can also generate plots.


## Initial Setup
### Requirements
This guide assumes you already have Python 3, pip, git and R installed. If not, install them.

The following packages are used in this script. Install with pip.
```sh
pip install pathlib arrow fuzzywuzzy pandas folium tqdm
```

- arrow - offers a sensible, human-friendly approach to creating, manipulating, formatting and converting dates, times, and timestamps.
- pathlib - support for OS-agnostic file system manipulation. Allows script to run on Windows, Unix, Mac, etc...
- fuzzywuzzy - fuzzy string matching, used to find files even when they don't exactly match.
- pandas - powerful Python data analysis toolkit.
- folium - visualize GPS data on a Leafleft map via Folium. Uses Open Street Map.
- tqdm - provides progress bars on the command line.

#### Create a directory to process ride data and clone the scripts from github
```sh
mkdir Post_Processing Scripts
cd Post_Processing Scripts
mkdir _Unprocessed_Data
git clone https://github.com/pdailey/Bike_Crash_Post_Processing
```

## Processing Data
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

The current implementation can only handle one ride at a time, AKA don't place 2 imu.csv files into the directory.

### Run the script
Run the script from the command line:
```sh
python Process_Ride_Data.py
```

The script will create a save directory using the following timestamp format `_Processed_Data/MM.DD.YYY@HH.MM`. Yes, this is a terrible format, but like all things that are written in code, it too can change...

If there are no errors, the following csv files should be in the directory:
```
├── accelerometer.csv   # Raw Accelerometer Data
├── angles.csv          # Euler Angles
├── angular_rates.csv   # Euler Angular Rates
├── cadence.csv         # Cadence
├── calibration.csv     # Calibration Values
├── front_brake.csv     # Front Brake Engagement
├── gps.csv             # GPS Lat/Long
├── gyroscope.csv       # Raw Gyroscope Data
├── imu.csv             # ALL Imu Data
├── rear_brake.csv      # Rear Brake Engagement
├── route_map.html      # GPS coordinates mapped in the browser
├── steering.csv        # Steering Angle
└── wheelspeed.csv      # Wheelspeed
```


