
# coding: utf-8

# # Open Files 
# Open the files for processing. Create a save directory using the timestamp from the calibration CSV. 

# In[1]:

import os
import fnmatch
from pathlib import *
import arrow

# Expected files from a single ride
logs = ["calibration.csv",         "cadence.csv",        "front_brake.csv",         "rear_brake.csv",         "imu.csv",         "steering.csv",         "wheelspeed.csv"]

# Directories to organize data
p = Path('.').resolve()

open_dir = 'Unprocessed_Data'
save_dir = 'Processed_Data'
temp_dir = 'temp'

# Set Default Datetime to name folder where logs are stored
now = arrow.utcnow().to("US/Pacific")
print("BEGIN PROCESSING DATA")
print("Data processed on {} at {}".format(now.format('MM/DD/YYYY'), now.format('HH:mm:ss')))

now = str(now.format('MM.DD.YYYY@HH.mm'))

'''
# TODO: IMPLEMENT WITH RTC ONBOARD. This will change the order of the 
# Get the time that the ride took place from the calibration 
# routine and make a save directory for the files
for file in os.listdir(str(open_path)):
    if fnmatch.fnmatch(file, "*" + logs[0]):
        d = os.path.basename(file).split('_')[0]
'''

open_path = p / open_dir
temp_path = p / temp_dir
save_path = p / save_dir / now

# Throw error if the temp/save directories already exist.
temp_path.mkdir(exist_ok = False) 
save_path.mkdir(exist_ok = False)

#print("Processed files will be saved to: \n{}" .format(save_path))


# # Find the files to process
# Use fuzzy searching to robustly find the logs to process in the open folder (members of the team have difficulty naming things consistently). Fuzzy search implements the Levenshtein distance algorithm.

# In[2]:

from fuzzywuzzy import process

files = os.listdir(str(open_path))

print("\n\nLOOKING FOR FILES IN:\n{}".format(open_path))
print("Moving to {}".format(temp_path))

# Search a file that matches each log we are looking for
for log in logs:
    print("\t{}".format(log))
    # find the top match
    file = process.extractOne(log, files)
    
    src = open_path / file[0]
    dest = temp_path / log
    os.rename(str(src), str(dest))
    print('\t{0:3d}% match. Rename {2} --> {1}\n'.format(file[1], log, file[0]))


# # Parse IMU/GPS Strings
# Functions to parse the IMU/GPS strings

# In[3]:

'''Parses useful data from the GPS Position Packet and appends to a list
The NMEA GPS pose packet contains GPS latitude, longitude, and 
altitude in addition to Euler Angle attitude and GPS heading.

Packet Format:
$PCHRG,time,latitude,longitude,altitude,roll,pitch,yaw,heading,*checksum
'''
def parsePositionString(p):
    if(len(p) >= 8):
        # GPS was running, avoid null island. 
        if(p[2] != "0.000000"): 
            gps = ""
            # time, lat, long
            gps += p[1] + ", "
            # [lat, long]
            gps += p[2] + ", " + p[3]
            lst_gps.append(gps)
            
            angle = ""
            # [time, pitch angle, roll angle, yaw angle]
            angle = p[1] +", "+ p[5] +", "+ p[6] + ", "+ p[7]
            lst_angle.append(angle)
             
            

            
            
''' Parses useful data from the Rate Packet and appends to a list
The NMEA rate packet contains angular rates and GPS velocities measured 
by the sensor, if GPS is present.

Packet Format:
$PCHRR,time,vn,ve,vup,roll_rate,pitch_rate,yaw_rate,*checksum
'''
def parseRateString(p):
    if(len(p) >= 8):
        rate = ""
        # time
        rate += p[1] + ", "
        # [pitch rate, roll rate, yaw rate]
        rate += p[5] + ", " + p[6] + ", " + p[7] 
        lst_rate.append(rate)
 
'''Parses useful data from the Sensor Packet and appends to a list
The NMEA sensor packet contains gyro, accelerometer, and magnetometer 
data measured by the sensor.

Packet Format:
$PCHRS,count,time,sensor_x,sensor_y,sensor_z,*checksum
'''
def parseSensorString(p):  
    if(len(p) == 7):
        rate = ""
        # time
        rate += p[2] + ", "
        # [sensor x, y, z]
        rate += p[3] + ", " + p[4] + ", " + p[5] 
        
        # Save to proper file. Magnotometer data is discarded
        sensor = int(p[1])   
        if(sensor == 0):
            lst_gyro.append(rate)
        elif(sensor == 1):
            lst_accel.append(rate)
            


# # Process the IMU/GPS File

# In[4]:

import csv
import re
import fileinput
from tqdm import tqdm

# List of data that will be seperated into seperate CSV files
# Initial entries are headers.
lst_accel = []
lst_gyro = []
lst_gps = []
lst_angle = []
lst_rate = []
lst_accel.append("time,x_accel,y_accel,z_accel")
lst_gyro.append("time,x_gyro,y_gyro,z_gyro")
lst_gps.append("time,lat,long")
lst_angle.append("time,pitch_angle,roll_angle,yaw_angle")
lst_rate.append("time,pitch_rate,roll_rate,yaw_rate")

print("\n\nPROCESSING IMU")
# Search for $ character that denotes NMEA sentences in a given csv file. 
# Does not filter data after the checksum, as correct NMEA 
# sentences end with a newline chracter
imu_file = str(temp_path) + "/" + logs[4]

# Currently the IMU data is a little scrambled. Fixed with the following hack...
for line in fileinput.input(imu_file, inplace=True):
    # inside this loop the STDOUT will be redirected to the file
    # the comma after each print statement is needed to avoid double line breaks
    print(line.replace("$", "\n$"),)
    

# Get a list of strings to parse
strings = [re.findall(r'[A-Z]{5}\S*', line) for line in open(imu_file)]

# We only care about non-empty strings
strings = filter(None, strings)
  
print("Parsing IMU Packets...")
# Filter lines by NMEA type
for string in tqdm(strings):
    # Seperate into parsable data
    string = [x.strip() for x in string[0].split(',')] 
    
    # Switch Statement to handle different data packets
    if(string[0] == "PCHRG"):
        parsePositionString(string)
    elif(string[0] == "PCHRR"):
        parseRateString(string)
    elif(string[0] == "PCHRS"):
        parseSensorString(string)      
        
print("Done.")


# # Extract position and rates from IMU

# In[5]:

import fnmatch
import os

# Save the parsed sentences
def saveFile(lst, file, dest):
    with open(file, "w") as f:
        for line in lst:
            f.write("%s\n" % line)
    
    dest = dest / file
    os.rename(file, str(dest))
    print('\tSaved {0} --> {1}'.format(file, dest.relative_to(p)))
            

# Save extracted lists to data files
print("Extracting GPS, acceleration, euler angles and angular rates from imu.csv")
saveFile(lst_gps, "gps.csv", temp_path)
saveFile(lst_angle, "angles.csv", temp_path)
saveFile(lst_rate, "angular_rates.csv", temp_path)
saveFile(lst_gyro, "gyroscope.csv", temp_path)
saveFile(lst_accel, "accelerometer.csv", temp_path)


# # Map the GPS Route
# 
# The GPS route is mapped using folium and output as an html file

# In[7]:

import pandas as pd

print("\n\nMAPPING GPS")
src = temp_path / 'gps.csv'

# Read the data frame
df = pd.read_csv(str(src), index_col=None)
print('Loaded {0}'.format(src.relative_to(p)))

# Show the data
df.head(10)


# In[ ]:

# Map route from GPS data
import folium
from tqdm import tqdm

# Zero the time reported on the map
df['time'] - df['time'][0]

# map every nth lat/long point
nth = 5
print('Mapping every {}th point in a set of {}.'.format(nth, df.shape[0]))
print('This may take a while for large data sets...'.format(nth))

# center the map
start_pt = [df["lat"][0], df["long"][0]]
map_route = folium.Map(location = start_pt,
                       zoom_start=14,
                       tiles='Stamen Toner')

# tqdm gives a progess bar.
for index, row  in tqdm(df.iterrows()):
    if(index%nth == 0):
        # add info above marker
        # note, this time is the time since the gps was turned on. Not synchronized to other measurements.
        datum = "Time: " + str(df['time'][index]) + " sec"
        # format [lat, long]
        point = [df['lat'][index], df['long'][index]]
        folium.Marker(point, popup=datum).add_to(map_route)

#mappy = plotPoints(latlong, nth)
dest = temp_path / 'route_map.html'
map_route.save( str(dest))

print('Map saved to {}.'.format(dest.relative_to(p)))
map_route


# # Create Plots using R

# In[ ]:

import subprocess

rscript = p / "Plot_Ride_Data.R"

# make script executable. Uses octal form
# representation. needs an integer, not a string. 0777 == 511.
rscript.chmod(511)

# TODO - Set timeout?
subprocess.run("./Plot_Ride_Data.R | R --vanilla | less", shell=True, check=True, timeout = 10)


# # Save the files to a Time-Stamped Directory

# In[ ]:



# Save the remaining files 
print("\n\nSAVING FILES TO {}\n".format(save_path))

for file in os.listdir(str(temp_path)):
#    if fnmatch.fnmatch(file, '*.csv'):
    src = temp_path / file
    dest = save_path / file
    os.rename(str(src), str(dest))
    print('\tSaved {0} --> {1}'.format(src.relative_to(p), dest.relative_to(p)))

temp_path.rmdir()


# In[ ]:



