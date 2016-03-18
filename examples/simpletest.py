#!/usr/bin/env python

from ADS_80422.ADS80422 import ADS80422

import time
import logging

logging.basicConfig(level=logging.DEBUG)

rainPin = "P9_11"
anenometerPin = "P9_12"
directionPin = "P9_33"

# sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
# Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = ADS80422(anenometerPin, directionPin, rainPin)

weatherStation.set_acquisition_mode(SDL_MODE_SAMPLE, 5.0)
# weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)

totalRain = 0
while True:
    print "---------------------------------------- "
    print "----------------- "
    print " SDL_Pi_Weather_80422 Library"
    print " WeatherRack Weather Sensors"
    print "----------------- "

    currentWindSpeed = weatherStation.get_wind_speed()
    currentWindGust = weatherStation.get_wind_gust()
    totalRain += weatherStation.get_rain_total()

    print "Rain Total=\t%0.2f mm" % totalRain
    print "Wind Speed=\t%0.2f Km/h" % currentWindSpeed
    print "MPH wind_gust=\t%0.2f Km/h" % currentWindGust

    print "Wind Direction=\t\t %0.2f Degrees" % weatherStation.get_wind_direction()
    print "Wind Direction Voltage=\t %0.3f V" % weatherStation.get_wind_direction_voltage()

    print "----------------- "
    print "----------------- "

    time.sleep(5.0)
