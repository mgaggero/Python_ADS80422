# Copyright (c) 2015 Massimo Gaggero
# Author: Massimo Gaggero

# Based on: SDL__Pi_Weather_80422.py
# Raspberry Pi Python Library for SwitchDoc Labs WeatherRack.
# https://github.com/switchdoclabs/SDL_Pi_Weather_80422
# Created by SwitchDoc Labs February 13, 2015
# Released into the public domain.

# Adapted for BeagleBone Black and its internal ADC's

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC

import time
import logging

# #sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
ASYNC_MODE = 0
# #Delay mode means to wait for sampleTime and the average after that time.
BLOCKING_MODE = 1

WIND_FACTOR = 2.400


def fuzzy_compare(compare_value, value):
    VARYVALUE = 0.05

    if (value > (compare_value * (1.0 - VARYVALUE))) and (value < (compare_value * (1.0 + VARYVALUE))):
        return True

    return False


def micros():
    microseconds = int(round(time.time() * 1000000))
    return microseconds


class ADS80422:
    GPIO.setwarnings(False)

    pin_anem = 0
    pin_dir = 0
    pin_rain = 0

    _currentRainCount = 0
    _currentWindCount = 0
    _currentWindSpeed = 0.0
    _currentWindDirection = 0.0

    _lastWindTime = 0
    _lastRainTime = 0
    _shortestWindTime = 0
    _currentRainMin = 0

    _sampleTime = 5.0
    _selectedMode = ASYNC_MODE
    _startSampleTime = 0

    def __init__(self, pin_anem, pin_dir, pin_rain):
        self._logger = logging.getLogger('ADS80422.ADS80422')

        ADS80422.pin_anem = pin_anem
        ADS80422.pin_dir = pin_dir
        ADS80422.pin_rain = pin_rain

        GPIO.setup(pin_anem, GPIO.IN)
        GPIO.setup(pin_rain, GPIO.IN)

        # when a falling edge is detected on port pinAnem, regardless of whatever
        # else is happening in the program, the function callback will be run

        GPIO.add_event_detect(ADS80422.pin_anem,
                              GPIO.RISING,
                              callback=self._service_interrupt_anemometer,
                              bouncetime=20)
        GPIO.add_event_detect(ADS80422.pin_rain,
                              GPIO.RISING,
                              callback=self._service_interrupt_rain,
                              bouncetime=20)
        ADC.setup()

    def voltage_to_degrees(self, value, default_wind_direction):
        if fuzzy_compare(1.38, value):
            return 0.0

        if fuzzy_compare(0.71, value):
            return 22.5

        if fuzzy_compare(0.81, value):
            return 45

        if fuzzy_compare(0.15, value):
            return 67.5

        if fuzzy_compare(0.16, value):
            return 90.0

        if fuzzy_compare(0.12, value):
            return 112.5

        if fuzzy_compare(0.32, value):
            return 135.0

        if fuzzy_compare(0.22, value):
            return 157.5

        if fuzzy_compare(0.51, value):
            return 180

        if fuzzy_compare(0.43, value):
            return 202.5

        if fuzzy_compare(1.11, value):
            return 225

        if fuzzy_compare(1.05, value):
            return 247.5

        if fuzzy_compare(1.66, value):
            return 270.0

        if fuzzy_compare(1.45, value):
            return 292.5

        if fuzzy_compare(1.56, value):
            return 315.0

        if fuzzy_compare(1.24, value):
            return 337.5

        return default_wind_direction

    # ### Wind Direction Section ###
    def get_wind_direction(self):
        value = ADC.read(ADS80422.pin_dir)
        voltage_value = value * 1.8000
        direction = self.voltage_to_degrees(voltage_value, ADS80422._currentWindDirection)

        self._logger.debug('Current wind direction {0:.2f})'.format(direction))
        return direction

    def get_wind_direction_voltage(self):
        value = ADC.read(ADS80422.pin_dir)
        voltage_value = value * 1.8000

        self._logger.debug('Current wind direction voltage {0:.3f})'.format(voltage_value))
        return voltage_value

# 	def accessInternalCurrentWindDirection(self):
#    		return SDL_Pi_Weather_80422._currentWindDirection;

    # ### Wind Speed Section ###
    def set_acquisition_mode(self, selected_mode, sample_time):
        ADS80422._sampleTime = sample_time
        ADS80422._selectedMode = selected_mode

        if ADS80422._selectedMode == ASYNC_MODE:
            self._start_wind_sample(ADS80422._sampleTime)

    def _start_wind_sample(self, sample_time):
        ADS80422._startSampleTime = micros()
        ADS80422._sampleTime = sample_time

    def _get_wind_speed_when_sampling(self):
        compare_value = ADS80422._sampleTime * 1000000

        if (micros() - ADS80422._startSampleTime) >= compare_value:
            # sample time exceeded, calculate currentWindSpeed
            time_span = micros() - ADS80422._startSampleTime

            ADS80422._currentWindSpeed = (float(ADS80422._currentWindCount)/float(time_span)) * WIND_FACTOR * 1000000.0
            ADS80422._currentWindCount = 0
            ADS80422._startSampleTime = micros()

        return ADS80422._currentWindSpeed

    def get_wind_speed(self):
        if ADS80422._selectedMode == ASYNC_MODE:
            ADS80422._currentWindSpeed = self._get_wind_speed_when_sampling()
        else:
            # km/h * 1000 msec
            ADS80422._currentWindCount = 0
            # delay(ADS80422._sampleTime*1000)
            ADS80422._currentWindSpeed = (float(ADS80422._currentWindCount)/float(ADS80422._sampleTime)) * WIND_FACTOR

        return ADS80422._currentWindSpeed

    def get_wind_gust(self):
        latest_time = ADS80422._shortestWindTime / 1000000.0
        ADS80422._shortestWindTime = 0xffffffff

        if latest_time == 0:
            return 0
        else:
            return (1.0 / float(latest_time)) * WIND_FACTOR

    def reset_wind_gust(self):
        ADS80422._shortestWindTime = 0xffffffff

    # ### Rain Section ###
    def get_rain_total(self):
        # mm of rain - we get two interrupts per bucket
        rain_amount = 0.2794 * float(ADS80422._currentRainCount)
        ADS80422._currentRainCount = 0
        return rain_amount

    def reset_rain_total(self):
        ADS80422._currentRainCount = 0

    def _service_interrupt_anemometer(self, channel):
        self._logger.debug('Service Interrupt Anenmometer: {0:s})'.format(channel))

        current_time = micros() - ADS80422._lastWindTime
        ADS80422._lastWindTime = micros()

        if current_time > 1000:
            ADS80422._currentWindCount += 1

            if current_time < ADS80422._shortestWindTime:
                ADS80422._shortestWindTime = current_time

    def _service_interrupt_rain(self, channel):
        self._logger.debug('Service Interrupt Rain: {0:s})'.format(channel))

        current_time = micros() - ADS80422._lastRainTime
        ADS80422._lastRainTime = micros()

        if current_time > 500:
            ADS80422._currentRainCount += 1
            if current_time < ADS80422._currentRainMin:
                ADS80422._currentRainMin = current_time
