#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""Convert differential inputs on an Raspberry Pi and an ADS 1256
"""

# Python Imports
from os import path
import time          # For setting up the Sampling Frequency
import argparse      # For Parsing Commandline Arguments

# Physical Computing Imports
import ads               # Talking to the ADS1256
import RPi.GPIO as GPIO  # GPIO interactions

# 3rd Party Imports


# --- Script Setup ---------------------------------------------------------- #
# Get the Start Time
START_TIME = time.time()


# --- Get the ADC ----------------------------------------------------------- #
def getadc():
    
    # Initialize
    adc = ads.ADS1256()     # Creates the Interface Object in Python
    adc.ADS1256_init()      # Initializes the ADC
    adc.ADS1256_SetMode(1)  # Sets to Differential Measurements
    return adc


# --- Main Script ----------------------------------------------------------- #
if __name__ == '__main__':
    
    # --- Argument Parser --------------------------------------------------- #
    # Setup the Argument Parser
    prsr = argparse.ArgumentParser(description=__doc__)

    # Add Arguments
    prsr.add_argument(
        '-c', '--channels', default='0', type=str, metavar='chnls',
        help='''A comma separated string of differential channels to read.
        For example, a value of "0" will read the differential voltage across
        AD0/AD1. A value of "0,1" will read the differential voltage across
        AD0/AD1 and AD2/AD3.'''
    )
    prsr.add_argument(
        '-n', '--names', default=None, type=str,
        help='''A comma separated string of the differential channels names.
        This amounts to what the channel column headers should be in the
        stdout or output file.'''
    )
    prsr.add_argument(
        '-f', '--file', default=None, type=str,
        help='The output file name. Default (no input) writes to stdout.'
    )
    prsr.add_argument(
        '-o', '--overwrite', action='store_true',
        help='Gives permission to clobber/overwrite the output file.'
    )
    prsr.add_argument(
        '-s', '--frequency', default=1., type=float, metavar='f',
        help='Sets the sampling frequency (in Hz) between reads.'
    )

    # Mutually Exclusive Group of Exit Criteria
    exitCri = prsr.add_mutually_exclusive_group()
    exitCri.add_argument(
        '-i', '--maxiter', default=2**16, type=int, metavar='i',
        help='''The maximum number of read/write iterations to execute.
                Default: 65536'''
    )
    exitCri.add_argument(
        '-t', '--maxtime', default=3600., type=float, metavar='t',
        help='''The maximum length of time (in s) of read/write iterations to execute.
                Default: 3600'''
    )

    # Parse
    args = prsr.parse_args()

    # Check/Change Arguments
    # Get the Channels to Read
    CHANS = list(map(int, args.channels.split(',')))

    # Check Valid Channels
    for c in CHANS:
        if c not in range(4):
            raise ValueError(f'{c} is not a valid channel number. Valid numbers are [0-3].')
    
    # Set the Channel Names if not Provided / Else Check
    if args.names is None:
        NAMES = [f'Channel {c}' for c in CHANS]
    elif len(CHANS) != len(args.names.split(',')):  # If # CHAN does not equal # Names
        raise ValueError('Number of channel names does not match number of channels.')
    else:  # Other wise store the given names
        NAMES = [n.strip() for n in args.names.split(',')]
    
    # Set the Output File
    OUT_FN = args.file
    if OUT_FN is not None and (path.exists(OUT_FN) and not args.overwrite):
        raise ValueError(
            f'File "{OUT_FN}" already exists.\n\tChange the file name or add the overwrite flag.'
        )
    
    # Set the Read Delta Time
    READ_DT = 1/args.frequency
    
    # Get the ADC
    adc = getadc()
    while(1):
        ADC_Value = adc.ADS1256_GetAll()
        print ("0 ADC = %lf"%(ADC_Value[0]))
        print ("1 ADC = %lf"%(ADC_Value[1]))
        print ("2 ADC = %lf"%(ADC_Value[2]))
        print ("3 ADC = %lf"%(ADC_Value[3]))
        time.sleep(READ_DT)
        print ("\33[9A")
