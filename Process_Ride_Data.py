from fuzzywuzzy import process
from pathlib import *
from tqdm import tqdm
import arrow
import csv
import fileinput
import fnmatch
import folium
import os
import pandas as pd
import re
import subprocess


'''
Validate Checksum

Count of the number of bits in a packet that is included with the packet
to check whether the same number of bits arrived. If the counts match,
it's assumed that the complete transmission was received and the data is
valid.
'''


def validChecksum(st):
    try:
        # Split the string into the data and the checksum
        packet, checksum = st.split(",*")
        # convert to hex for XOR comparison
        checksum = int(checksum, 16)
        # Remove leading $ symbol and commas
        packet = packet[1:].replace(',', '')
        # perform checksum XOR
        packet_sum = 0
        for char in packet:
            packet_sum ^= ord(char)
        if(packet_sum == checksum):
            return True
        else:
            return False
    except:
        return False

'''Parses useful data from the GPS Position Packet and appends to a list
The NMEA GPS pose packet contains GPS latitude, longitude, and
altitude in addition to Euler Angle attitude and GPS heading.

Packet Format:
$PCHRG,time,latitude,longitude,altitude,roll,pitch,yaw,heading,*checksum
'''


def parsePositionString(p, time_zero):
    if(len(p) > 6):
        # GPS was running, avoid null island.
        if(p[2] != "0.000000"):
            p[1] = str(float(p[1]) - time_zero)
            # time, lat, long
            s = p[1] + ", " + p[2] + ", " + p[3]
            lst_gps.append(s)

        # time, pitch angle, roll angle, yaw angle
        s = str(p[1]) + ", " + p[5] + ", " + p[6] + ", " + p[7]
        lst_angle.append(s)

''' Parses useful data from the Rate Packet and appends to a list
The NMEA rate packet contains angular rates and GPS velocities measured
by the sensor, if GPS is present.

Packet Format:
$PCHRR,time,vn,ve,vup,roll_rate,pitch_rate,yaw_rate,*checksum
'''


def parseRateString(p, time_zero):
    if(len(p) > 6):
        # GPS Velocity
        # time, north velocity, east velocity
        p[1] = str(float(p[1]) - time_zero)
        s = p[1] + ", " + p[2] + ", " + p[3]
        lst_gps_vel.append(s)

        # Rates: pitch roll and yaw
        # time, pitch rate, roll rate, yaw rate
        s = p[1] + ", " + p[5] + ", " + p[6] + ", " + p[7]
        lst_rate.append(s)


'''Parses useful data from the Sensor Packet and appends to a list
The NMEA sensor packet contains gyro, accelerometer, and magnetameter
data measured by the sensor.

Packet Format:
$PCHRS,count,time,sensor_x,sensor_y,sensor_z,*checksum
'''


def parseSensorString(p, time_zero):
    if(len(p) > 4):
        p[2] = str(float(p[2]) - time_zero)
        # time, sensor x, sensor y, sensor z
        s = p[2] + ", " + p[3] + ", " + p[4] + ", " + p[5]

        # Save to proper file.
        sensor = int(p[1])
        if(sensor == 0):
            lst_gyro.append(s)
        elif(sensor == 1):
            lst_accel.append(s)
        elif(sensor == 2):
            lst_mag.append(s)

''' Parses useful data from the Health Packet and appends to a list.
The NMEA health packet contains a summary of health-related information,
including basic GPS information and sensor status information.

Packet Format:
$PCHRH,time,sats_used,sats_in_view,HDOP,mode,COM,accel,gyro,mag,GPS,res,res,res,*checks um
'''


def parseHealthString(p, time_zero):
    return False
    # TODO, left for compatibility


'''
Saves a list to a file in a given directory
'''


def saveListToFile(lst, file, dest):
    with open(file, "w") as f:
        for line in lst:
            f.write("%s\n" % line)
    dest = dest / file
    os.rename(file, str(dest))
    print('\tSaved {0} --> {1}'.format(file, dest.relative_to(p)))


'''
User Defined Variables
'''
# Set true to graph the data using R
graphing = False

# Set the the packet rates
pkt_Hz = 20  # position packet update rate Hz
gps_Hz = 5  # gps update rate Hz


'''
Open Files
Open the files for processing. Create a save directory using the time the data was processed
'''

# Expected files from a single ride
logs = [
    "calibration.csv",
    "cadence.csv",
    "front_brake.csv",
    "rear_brake.csv",
    "imu.csv",
    "steering.csv",
    "wheelspeed.csv"
]

# Set Default Datetime to name folder where logs are stored
now = arrow.utcnow().to("US/Pacific")
now = str(now.format('MM.DD.YYYY@HH.mm'))

# Directories
p = Path('.').resolve()
open_dir = '_Unprocessed_Data'
temp_dir = '_temp'
save_dir = '_Processed_Data'

# Paths
open_path = p / open_dir
temp_path = p / temp_dir
save_path = p / save_dir / now

print("BEGIN PROCESSING DATA")
print("Data processed on {}".format(now))
print("Processed files will be saved to: \n{}" .format(save_path))

# Throw error if the temp/save directories already exist.
temp_path.mkdir(exist_ok=False)
save_path.mkdir(exist_ok=False)

'''
Find the files to process
Use fuzzy searching to robustly find the logs to process in the open
folder (members of the team have difficulty naming things consistently).
Fuzzy search implements the Levenshtein distance algorithm.
'''
files = os.listdir(str(open_path))

print("\n\nLOOKING FOR FILES IN:\n{}".format(open_path))
print("\n MOVING TO:\n{}".format(temp_path))

# Search a file that matches each log we are looking for
for log in logs:
    print("\t{}...".format(log))
    # find the top match
    file = process.extractOne(log, files)
    src = open_path / file[0]
    dest = temp_path / log
    os.rename(str(src), str(dest))
    print('\t{0:3d}% match. Rename {2} --> {1}'.format(file[1], log, file[0]))

'''
Convert BBB Time
The BBB stores the time the testing started in calibration.csv. This
time is not correct, at the BBB does not have an RTC installed
currently. Instead, the times are converted to seconds since
calibration, and converted from ms to s.
'''

# get the start time from the calibration routine
src = temp_path / logs[0]
df = pd.read_csv(src, index_col=None)
t_0 = df["Time Zero"][0]
print("Calibrating the time for the following files...")

for log in logs:
    # Skip calibration and imu. Calibration is not a log file,
    # imu it is on an arduino with a an independent system time.
    if(log != "calibration.csv" and log != "imu.csv"):
        print("\t{}".format(log))
        csv = temp_path / log
        df = pd.read_csv(csv, index_col=None)
        # get delta t, and convert from ms to s
        df["Time"] = (df["Time"] - t_0) / 1000
        df.to_csv(str(csv), index_col=None)


'''
Process the IMU/GPS File
'''
# List of data that will be separated into separate CSV files.
lst_accel = []
lst_accel.append("time,x_accel,y_accel,z_accel")
lst_angle = []
lst_angle.append("time,pitch_angle,roll_angle,yaw_angle")
lst_gps = []
lst_gps.append("time,lat,long")
lst_gps_vel = []
lst_gps_vel.append("time,vel_east,vel_west")
lst_gyro = []
lst_gyro.append("time,x_gyro,y_gyro,z_gyro")
lst_mag = []
lst_mag.append("time,,x_magnetometer,y_magnetometer,z_magnetometer")
lst_rate = []
lst_rate.append("time,pitch_rate,roll_rate,yaw_rate")

print("\n\nPROCESSING IMU PACKETS")

# Read the file as a list of strings deliniated by newlines.
imu_file = str(temp_path) + "/" + logs[4]
strings = [line.rstrip('\n') for line in open(imu_file)]

bad_packets = 0
total_packets = 0
t_0 = 0

for s in tqdm(strings):
    total_packets += 1

    if(validChecksum(s)):
        # Seperate into a list to parse
        s = [x.strip() for x in s.split(',')]

        # Synchronize the time difference between the IMU and the BBB
        if(t_0 == 0):
            if(s[0] == "$PCHRS"):
                t_0 = float(s[2])
            else:
                t_0 = float(s[1])

        # Filter lines by NMEA type
        elif(t_0 != 0):
            if(s[0] == "$PCHRG"):
                parsePositionString(s, t_0)
            elif(s[0] == "$PCHRR"):
                parseRateString(s, t_0)
            elif(s[0] == "$PCHRS"):
                parseSensorString(s, t_0)
            elif(s[0] == "$PCHRH"):
                parseHealthString(s, t_0)
            else:
                bad_packets += 1
    else:
        bad_packets += 1


percent_success = 100 * (1 - bad_packets / total_packets)
print("\RESULTS:")
print("\t{} packets processed. ".format(total_packets))
print("\t{} of these were corrupted or not identified".format(bad_packets))
print("\t{:3.2f}% packets sucessfully identified and processed".format(
    percent_success))


# Save extracted lists to data files
print("Extracting GPS, acceleration, euler angles and angular rates from parsed IMU packets.")
saveListToFile(lst_gps, "gps.csv", temp_path)
saveListToFile(lst_gps_vel, "gps_vel.csv", temp_path)
saveListToFile(lst_angle, "angles.csv", temp_path)
saveListToFile(lst_rate, "angular_rates.csv", temp_path)
saveListToFile(lst_gyro, "gyroscope.csv", temp_path)
saveListToFile(lst_accel, "accelerometer.csv", temp_path)


# # Map the GPS Route
# The GPS route is mapped using folium and output as an html file

print("\n\nMAPPING GPS")
src = temp_path / 'gps.csv'

# Read the data frame
print('Loaded {0}'.format(src.relative_to(p)))
df = pd.read_csv(str(src), index_col=None)
df = df.apply(lambda x: pd.to_numeric(x, errors='coerce'))

# remove intervals between gps updates
df = df[::int(pkt_Hz / gps_Hz)]

# map every nth lat/long point
time_period = 3  # seconds
nth = time_period * gps_Hz

print('Mapping every {}th point in a set of {}.'.format(nth, df.shape[0]))
print('GPS is sampling at {0}Hz, {1}s between points.'.format(
    gps_Hz, time_period))
print('This may take a while for large data sets...')

# center the map
start_pt = [df["lat"][0], df["long"][0]]
map_route = folium.Map(location=start_pt,
                       zoom_start=14,
                       tiles='Stamen Toner')

# map point by point
for index, row in tqdm(df.iterrows()):
    if(index % nth == 0):
        # add info above marker
        datum = "Time: " + str(df['time'][index]) + " sec"
        point = [df['lat'][index], df['long'][index]]

        # Make start point a different color
        if(index == 0):
            folium.Marker(point, popup='Start', icon=folium.Icon(color='red',icon='info-sign')).add_to(map_route)
        else:
            folium.Marker(point, popup=datum).add_to(map_route)


# Save the map as an HTML file
dest = temp_path / 'route_map.html'
map_route.save(str(dest))
print('Map saved to {}.'.format(dest.relative_to(p)))

# Create Plots using R
if(graphing):
    rscript = p / "Plot_Ride_Data.R"

    # make script executable. Uses octal form
    # representation. needs an integer, not a string. 0777 == 511.
    rscript.chmod(511)

    print("\n\nGENERATING PLOTS IN R")
    print('This may take a while...')

    # TODO - Set timeout?
    subprocess.run("./Plot_Ride_Data.R | R --vanilla | less",
                   shell=True, check=True, timeout=120)
    print("Plots saved to R_Plots.pdf")


# Save the remaining files
print("\n\nSAVING FILES TO {}\n".format(save_path))

for file in os.listdir(str(temp_path)):
    src = temp_path / file
    dest = save_path / file
    os.rename(str(src), str(dest))
    print('\tSaved {0} --> {1}'.format(src.relative_to(p),
                                       dest.relative_to(p)))

# Remove the temporary directory
temp_path.rmdir()
