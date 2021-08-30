'''
	sumall.py - script to sum all Ecoblock doe2 energy profiles and add diversity
	Ecoblock EPIC Project
	Date - 10/17/17
	Author - Leo Rainer
'''

# imports
import pandas as pd
import argparse
import glob
import numpy as np
import matplotlib.pyplot as plt

# read a doe2 hourly plant file and shift the non-hvac loads a number of hours
# name - name of file to read
# shift - hours to shift
# returns - 8760 series
def read_doe2(name, shift):
    if "B16" in name or "B19" in name:
        # MF runs are just plant
        skiprow = 0
        skipfoot = 0
    else:
        # SF runs have system first and have a spurious row at the end for some reason
        skiprow = 8760
        skipfoot = 1
    col_names = ['month', 'day', 'hour', 'total', 'heat', 'dhw', 'vent', 'equip', 'light', 'cool']
    df = pd.read_table(name, sep='\s+', skiprows=skiprow, names=col_names, skipfooter=skipfoot, engine='python')
    df.index = pd.date_range("1/1/17", periods=8760, freq="1H")
    #df.heat = df.heat.clip(0, df['2017-05']['heat'].max())  # remove supplemental heat
    total = df.heat + df.cool
    for end_use in ('dhw','vent','equip','light'):
        total = total + np.roll(df[end_use],shift)
    return total
    
# Arguments
parser = argparse.ArgumentParser(description = 'Ecoblock hourly profiles')
parser.add_argument('folder_name', help='DOE2 hourly data folder')
parser.add_argument('-s', dest='shift', default=0, help='max shift hours (default = 0)')
parser.add_argument('-f', dest='fraction', default=1, help='fraction of house load (default = 1)')
args = parser.parse_args()

total = np.zeros(8760)
max_shift = int(args.shift)
fraction = float(args.fraction)
outfile = "{0}_s{1:d}_f{2:2d}.sum".format(args.folder_name, max_shift, int(fraction * 100))

shift = 0
for file in glob.glob(args.folder_name + "/B*.hly"):
	shift = shift + 1
	if shift > max_shift:
		shift = -max_shift
	d2 = read_doe2(file, shift)
	print "Building {}: shift={} sum={}, min={}, max={}, std={}".format(file, shift, d2.sum(), d2.min(), d2.max(), d2.std())
	total = total + d2

# add in MF DHW
dhw = np.random.rand(8760)
total = total + dhw * 2 * 0.78  # B16
dhw = np.random.rand(8760)
total = total + dhw * 2 * 1.07  # B19

total = total * fraction

print "Total for {}: sum={}, min={}, max={}, std={}".\
	format(outfile,total.sum(), total.min(), total.max(), total.std())
np.savetxt(outfile,total,fmt="%1.1f")
	
