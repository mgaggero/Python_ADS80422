from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name 				= 'Python_ADS80422',
	  version 			= '1.0.0',
	  author			= 'Massimo Gaggero',
	  author_email		= '',
	  description		= 'Python Library for accessing the Argent Data Systems ADS-WS1 Weather Station on Beaglebone Black.',
	  license			= 'MIT',
	  url				= 'https://github.com/mgaggero/Python_ADS80422/',
	  dependency_links	= ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5'],
	  install_requires	= ['Adafruit-GPIO>=0.6.5'],
	  packages 			= find_packages())
