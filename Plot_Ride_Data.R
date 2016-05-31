#!/usr/bin/env Rscript

# ClearWorkspace
rm(list= ls())
  
# Control shift c to comment out a block of code
  
#########################################################################
# LIBRARIES
#########################################################################
library(latex2exp)
library(ggplot2)
library(reshape2)
library(ggthemes)
theme_set(theme_bw(base_size = 12, base_family = "Helvetica"))
attr(theme_bw, "complete")
library(plyr)


#########################################################################
# Set Working Directory
#########################################################################
d1 = getwd()
d2 = "/_temp"
dir = paste(d1, d2, sep = "")
setwd(dir)

########################################################################
# Acceleration
########################################################################
df_accel = read.csv("accelerometer.csv", header = T)
m_accel <-  melt(df_accel, id = "time")

plot <- ggplot(data = m_accel, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_point() +
  ggtitle("Raw Acceleration") +
  ylab(TeX('Acceleration, g')) +
  xlab(TeX('Time, s')) +
  ylim(-2, 2)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Acceleration_Raw.png", width = 8, height = 6)

plot <- ggplot(data = m_accel, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_smooth() +
  ggtitle("Raw Acceleration") +
  ylab(TeX('Acceleration, g')) +
  xlab(TeX('Time, s')) +
  ylim(-2, 2)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Acceleration_Smooth.png", width = 8, height = 6)

########################################################################
# Gyro
########################################################################
df_gyro = read.csv("gyroscope.csv", header = T)
m_gyro <-  melt(df_gyro, id = "time")

plot <- ggplot(data = m_gyro, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_point() +
  ggtitle("Raw Gyroscope") +
  ylab(TeX('Acceleration, deg/s')) +
  xlab(TeX('Time, s')) +
  ylim(-10, 10)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Gyroscope_Raw.png", width = 8, height = 6)

plot <- ggplot(data = m_gyro, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_smooth() +
  ggtitle("Gyroscope") +
  ylab(TeX('Acceleration, deg/s')) +
  xlab(TeX('Time, s')) +
  ylim(-10, 10)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Gyroscope_Smooth.png", width = 8, height = 6)

########################################################################
# Euler Angles and Rates
########################################################################
df_position = read.csv("angles.csv", header = T)
df_angular_rates = read.csv("angular_rates.csv", header = T)

m_position <-  melt(df_position, id = "time")
m_angular_rates <- melt(df_angular_rates, id = "time")

plot <- ggplot(data = m_position, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_smooth() +
  ggtitle("Euler Angles") +
  ylab(TeX('Angle, deg')) +
  xlab(TeX('Time, s')) +
  ylim(-10, 10)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Angles_Smooth.png", width = 8, height = 6)

plot <- ggplot(data = m_position, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_point() +
  ggtitle("Euler Angles") +
  ylab(TeX('Angle, deg')) +
  xlab(TeX('Time, s')) +
  ylim(-20, 20)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Angles_Raw.png", width = 8, height = 6)

plot <- ggplot(data = m_angular_rates, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_smooth() +
  ggtitle("Angular Rates") +
  ylab(TeX('Angular Velocity, deg/s')) +
  xlab(TeX('Time, s')) +
  ylim(-10, 10)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Rates_Smooth.png", width = 8, height = 6)

plot <- ggplot(data = m_angular_rates, aes( x = time, y = value, group = variable, colour = variable)) +
  geom_point() +
  ggtitle("Angular Rates") +
  ylab(TeX('Angular Velocity, deg/s')) +
  xlab(TeX('Time, s')) +
  ylim(-100, 100)
# Set Colors
plot = plot + scale_color_manual(values = c("#01665e", "#5ab4ac", "#2b8cbe", "#2b8cbe"))
plot
ggsave(plot, file = "Rates_Raw.png", width = 8, height = 6)

########################################################################
# front and rear brakes
########################################################################
df_front_brake = read.csv("front_brake.csv", header = T)
df_rear_brake = read.csv("rear_brake.csv", header = T)

# CALIBRATION
df_c = read.csv("calibration.csv", header = T)

## Convert the brake engagement to a percentage
df_front_brake$Flex.Sensor.Reading = 100 - 100 * ((df_c$Front.Engaged - df_front_brake$Flex.Sensor.Reading) / (df_c$Front.Engaged - df_c$Front.Disengaged))
df_rear_brake$Flex.Sensor.Reading  = 100 - 100 * ((df_c$Rear.Engaged  - df_rear_brake$Flex.Sensor.Reading) / (df_c$Rear.Engaged  - df_c$Rear.Disengaged))

## Scale the brake on/off
df_front_brake$Brake.Light.State <- df_front_brake$Brake.Light.State * 100
df_rear_brake$Brake.Light.State <- df_rear_brake$Brake.Light.State * 100

# Round to a number of decimal places
df_front_brake$Flex.Sensor.Reading <- round(df_front_brake$Flex.Sensor.Reading, digits = 2)
df_rear_brake$Flex.Sensor.Reading <- round(df_rear_brake$Flex.Sensor.Reading, digits = 2)

m_fb <- melt(df_front_brake, id = "Time")
m_rb <- melt(df_rear_brake, id = "Time")

# Plot all braking at once
# Plot two data frames simultaneously
plot <- ggplot(data = m_fb, aes( x = Time, y = value, group = variable, colour = variable)) +
  geom_line() +
  geom_line(data = m_rb, aes( x = Time, y = value, group = variable, colour = variable)) +
  ggtitle("Brake Values") +
  ylab(TeX('Percent Engagement')) +
  xlab(TeX('Time, s')) +
  ylim(-25, 100) +
  scale_color_manual(values = c("#fdae61", "#abd9e9", "#d7191c", "#2c7bb6"))
plot
ggsave(plot, file = "Brakes.png", width = 8, height = 6)

# Plot brakes individually
plot <- ggplot(data = m_fb, aes( x = Time, y = value, group = variable, colour = variable)) +
  geom_line() +
  ggtitle("Front Brake Values") +
  ylab(TeX('Percent Engagement')) +
  xlab(TeX('Time, s')) +
  ylim(-25, 100) +
  scale_color_manual(values = c("#01665e", "#2b8cbe"))
plot
ggsave(plot, file = "Front_Brake.png", width = 8, height = 6)

# Plot brakes individually
plot <- ggplot(data = m_rb, aes( x = Time, y = value, group = variable, colour = variable)) +
  geom_line() +
  ggtitle("Rear Brake Values") +
  ylab(TeX('Percent Engagement')) +
  xlab(TeX('Time, s')) +
  ylim(-25, 100) +
  scale_color_manual(values = c("#01665e", "#2b8cbe"))
plot
ggsave(plot, file = "Rear_Brake.png", width = 8, height = 6)


########################################################################
# steering angle
########################################################################
df_steering = read.csv("steering.csv", header = T)

# CALIBRATION
df_c = read.csv("calibration.csv", header = T)

## Convert the steering measurement to an angle
df_steering$Steering.Reading <- -90 + 180 * (df_c$Steering.Left - df_steering$Steering.Reading) / (df_c$Steering.Left - df_c$Steering.Right)

# Round to a number of decimal places
df_steering$Steering.Reading <- round(df_steering$Steering.Reading, digits = 2)

m_steering <- melt(df_steering, id = "Time")

# Steering Angle
plot <- ggplot(data = m_steering, aes( x = Time, y = value, group = variable, colour = variable)) +
  geom_point() +
  #geom_line() +
  ggtitle("Steering Angle") +
  ylab(TeX('Angle, degrees')) +
  xlab(TeX('Time, s')) +
  ylim(-120, 120) +
  scale_color_manual(values = c("#2b8cbe"))
plot
ggsave(plot, file = "Steering Angle.png", width = 8, height = 6)


#########################################################################
# wheelspeed
########################################################################
df_wheel = read.csv("wheelspeed.csv", header = T)

# Convert wheel RPM to m/s
# TODO: m/s, convert all wheel sizes to mm for this calculation
diameter <- .700 # 700cc
df_wheel$Velocity <- (df_wheel$Velocity * pi * diameter)/ 60

m_wheel <- melt(df_wheel, id = "Time")

plot <- ggplot(data = m_wheel, aes( x = Time, y = value, group = variable, colour = variable)) +
  geom_line() +
  geom_smooth() +
  ggtitle("Front Wheelspeed") +
  ylab(TeX('Velocity, m/s')) +
  xlab(TeX('Time, s')) +
  ylim(0, 10000) +
  scale_color_manual(values = c("#2b8cbe")) +
  theme(legend.position = "none")
plot
ggsave(plot, file = "Wheelspeed.png", width = 8, height = 6)


#########################################################################
# cadence
########################################################################
df_cadence = read.csv("cadence.csv", header = T)
m_cadence <- melt(df_cadence, id = "Time")

plot <- ggplot(data = m_cadence, aes( x = Time, y = value, group = variable, colour = variable))  +
  geom_point() +
  geom_smooth() +
  ggtitle("Cadence") +
  ylab(TeX('Cadence, RPM')) +
  xlab(TeX('Time, s')) +
  ylim(0, 150) +
  scale_color_manual(values = c("#2b8cbe")) +
  theme(legend.position = "none")
plot
ggsave(plot, file = "Cadence.png", width = 8, height = 6)