
# coding: utf-8

# # Open Files 
# Open the files for processing. Create a save directory using the timestamp from the calibration CSV. 

# In[1]:

import os
import fnmatch
from pathlib import *
import arrow

# Set true to graph the data using R
graphing = False
# Expected files from a single ride
logs = ["calibration.csv",         "cadence.csv",        "front_brake.csv",         "rear_brake.csv",         "imu.csv",         "steering.csv",         "wheelspeed.csv"]

# Directories to organize data
p = Path('.').resolve()

open_dir = '_Unprocessed_Data'
save_dir = '_Processed_Data'
temp_dir = '_temp'

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
print("\n MOVING TO:\n{}".format(temp_path))

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
    if(len(p) > 6):
        # GPS was running, avoid null island. 
        if(p[2] != "0.000000"): 
            # time, lat, long
            s = p[1] + ", " + p[2] + ", " + p[3]
            lst_gps.append(s)
         
        # time, pitch angle, roll angle, yaw angle
        s = p[1] +", "+ p[5] +", "+ p[6] + ", "+ p[7]
        lst_angle.append(s)
             
               
''' Parses useful data from the Rate Packet and appends to a list
The NMEA rate packet contains angular rates and GPS velocities measured 
by the sensor, if GPS is present.

Packet Format:
$PCHRR,time,vn,ve,vup,roll_rate,pitch_rate,yaw_rate,*checksum
'''
def parseRateString(p):
    if(len(p) > 6):
        # GPS Velocity
        # time, north velocity, east velocity
        s = p[1] + ", " + p[2] + ", " + p[3]
        lst_gps_vel.append(s)
        
        # Rates: pitch roll and yaw
        # time, pitch rate, roll rate, yaw rate
        s = p[1] + ", " + p[5] + ", " + p[6] + ", " + p[7] 
        lst_rate.append(s)
 

'''Parses useful data from the Sensor Packet and appends to a list
The NMEA sensor packet contains gyro, accelerometer, and magnetometer 
data measured by the sensor.

Packet Format:
$PCHRS,count,time,sensor_x,sensor_y,sensor_z,*checksum
'''
def parseSensorString(p): 
    if(len(p) > 4):
        # time, sensor x, sensor y, sensor z
        s = p[2] + ", " + p[3] + ", " + p[4] + ", " + p[5] 

        # Save to proper file. Magnotometer data is discarded
        sensor = int(p[1])   
        if(sensor == 0):
            lst_gyro.append(s)
        elif(sensor == 1):
            lst_accel.append(s)
            
''' Parses useful data from the Health Packet and appends to a list.
The NMEA health packet contains a summary of health-related information, 
including basic GPS information and sensor status information.


Packet Format:
$PCHRH,time,sats_used,sats_in_view,HDOP,mode,COM,accel,gyro,mag,GPS,res,res,res,*checks um
'''
def parseHealthString(p):
    return False
    #TODO, left for compatibility


# # Checksum
# Filter bad data.

# In[4]:

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


# # Process the IMU/GPS File

# In[5]:

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
lst_gps_vel = []
lst_accel.append("time,x_accel,y_accel,z_accel")
lst_gyro.append("time,x_gyro,y_gyro,z_gyro")
lst_gps.append("time,lat,long")
lst_angle.append("time,pitch_angle,roll_angle,yaw_angle")
lst_rate.append("time,pitch_rate,roll_rate,yaw_rate")
lst_gps_vel.append("time,vel_east,vel_west")

print("\n\nPROCESSING IMU PACKETS")

imu_file = str(temp_path) + "/" + logs[4]

strings = [line.rstrip('\n') for line in open(imu_file)]


# In[6]:

print("Parsing IMU Packets...")
# Filter lines by NMEA type
bad_packets = 0
total = 0
for string in tqdm(strings):
    total += 1
    
    if(validChecksum(string)):
        # Seperate into a list to parse
        string = [x.strip() for x in string.split(',')] 
        
        # Switch Statement to handle different data packets
        if(string[0] == "$PCHRG"):
            parsePositionString(string)
        elif(string[0] == "$PCHRR"):
            parseRateString(string)
        elif(string[0] == "$PCHRS"):
            parseSensorString(string) 
        elif(string[0] == "$PCHRH"):
            parseHealthString(string) 
        else:
            bad_packets += 1
    else:
        bad_packets += 1

        
percent_success = 100 * (1 - bad_packets/total)
        
print("\RESULTS:")
print("\t{} packets processed. ".format(total))
print("\t{} of these were corrupted or not identified".format(bad_packets))
print("\t{:3.2f}% packets sucessfully identified and processed".format(percent_success))


# In[7]:

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
print("Extracting GPS, acceleration, euler angles and angular rates from parsed IMU packets")
saveFile(lst_gps, "gps.csv", temp_path)
saveFile(lst_angle, "angles.csv", temp_path)
saveFile(lst_rate, "angular_rates.csv", temp_path)
saveFile(lst_gyro, "gyroscope.csv", temp_path)
saveFile(lst_accel, "accelerometer.csv", temp_path)


# # Extract position and rates from IMU

# # Map the GPS Route
# 
# The GPS route is mapped using folium and output as an html file

# In[8]:

import pandas as pd

print("\n\nMAPPING GPS")
src = temp_path / 'gps.csv'

# Read the data frame
df = pd.read_csv(str(src), index_col=None)
print('Loaded {0}'.format(src.relative_to(p)))

# Show the data
df.head(10)

# Show A summary of the data
#df.describe()
#df.head(n=10)
#df.dtypes


# In[ ]:




# In[9]:

# Map route from GPS data
import folium
from tqdm import tqdm

# Zero the sensor time, setting zero at when the tests began
# TODO: Convert all times....Currently handled in R
#df['time'] - df['time'][1]


# map every nth lat/long point
nth = 5
print('Mapping every {}th point in a set of {}.'.format(nth, df.shape[0]))
print('GPS is sampling at {0}Hz, {1}s between points.'.format(gps_Hz, time_period))
print('This may take a while for large data sets...')

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

# In[10]:

import subprocess

if(graphing):
    rscript = p / "Plot_Ride_Data.R"

    # make script executable. Uses octal form
    # representation. needs an integer, not a string. 0777 == 511.
    rscript.chmod(511)

    print("\n\nGENERATING PLOTS IN R")
    print('This may take a while...')


    # TODO - Set timeout?
    subprocess.run("./Plot_Ride_Data.R | R --vanilla | less", shell=True, check=True, timeout = 120)
    print("Plots saved to R_Plots.pdf")


# # Save the files to a Time-Stamped Directory

# In[11]:

# Save the remaining files 
print("\n\nSAVING FILES TO {}\n".format(save_path))

for file in os.listdir(str(temp_path)):
#    if fnmatch.fnmatch(file, '*.csv'):
    src = temp_path / file
    dest = save_path / file
    os.rename(str(src), str(dest))
    print('\tSaved {0} --> {1}'.format(src.relative_to(p), dest.relative_to(p)))

temp_path.rmdir()

