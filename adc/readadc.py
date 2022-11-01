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

# 3rd Party Imports
from tqdm import trange
import numpy as np
import pandas as pd


# --- Constants ------------------------------------------------------------- #
# Default Exit Criteria
MAX_ITER = 2**16
MAX_TIME = 3600.  # Seconds


# --- Get the ADC ----------------------------------------------------------- #
def getadc():
    """Gets the ADC object."""

    # Initialize
    adc = ads.ADS1256(scanMode=1)     # Creates the Interface Object in Python
    adc.init()                        # Initializes the ADC
    return adc


# --- Main Read Loop -------------------------------------------------------- #
def readloop(adc, channels=(0,), scale=1, readDT=1, startTime=np.inf,
             maxIter=MAX_ITER, maxTime=MAX_TIME):
    """The main loop to get the voltages from the channels"""

    # Initialize the Output
    output = []

    # Begin the Loop
    try:
        for i in trange(maxIter):

            # Get the Time Since Start
            readTime = time.time()
            readTimeStr  = time.strftime('%x %X', time.localtime(readTime))
            readTimeStr += str(readTime % 1)[1:6]
            startDT  = readTime - startTime
            if startDT >= maxTime:
                break

            # Get the Channel Data
            singleOutput  = [i+1, readTimeStr, startDT]
            singleOutput += [adc.GetChannalValue(c)*scale for c in channels]

            # Store
            output.append(singleOutput)

            # Wait
            time.sleep(readDT)

    except KeyboardInterrupt:
        print('Exiting Read Loop. Press again to exit script.')

    # Return the Output
    return output


# --- Write Output ---------------------------------------------------------- #
def writeoutput(output, chanNames, outFileName):

    # Convert to Pandas
    outDF = pd.DataFrame(
        data=output,
        columns=['Iter', 'Read Time', 'Start dt (s)'] + chanNames
    )
    outDF = outDF.set_index('Iter')

    # Write to File
    outDF.to_csv(outFileName)


# --- Main Script ----------------------------------------------------------- #
if __name__ == '__main__':

    # --- Script Constants -------------------------------------------------- #
    # Get the Start Time
    START_TIME = time.time()

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
    prsr.add_argument(
        '-v', '--vref', default=5, type=int, metavar='V', choices=(3, 5),
        help='''Sets the vref value for scaling analog inputs.
                Default: 5. Choices: 3 or 5'''
    )

    # Mutually Exclusive Group of Exit Criteria
    exitCri = prsr.add_mutually_exclusive_group()
    exitCri.add_argument(
        '-i', '--maxiter', default=MAX_ITER, type=int, metavar='i',
        help='''The maximum number of read/write iterations to execute.
                Default: 65536'''
    )
    exitCri.add_argument(
        '-t', '--maxtime', default=MAX_TIME, type=float, metavar='t',
        help='''The maximum length of time (in s) of read/write iterations to execute.
                Default: 3600'''
    )

    # Parse
    args = prsr.parse_args()

    # Constant Scale Value
    SCALE = args.vref/2**23

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

    # Get the Data & Write to File
    output = readloop(
        adc, channels=CHANS, scale=SCALE, readDT=READ_DT, startTime=START_TIME,
        maxIter=args.maxiter, maxTime=args.maxtime
    )
    writeoutput(output, NAMES, OUT_FN)
