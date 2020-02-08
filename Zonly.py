#!/usr/bin/env python3
# Python script intended to determine tool-to-tool offsets on a tool changing 3D printer
#   running a Duet 3 with Pi.
#
# This variant measures Z only. 
#
# Must run with root priviledge, such as via sudo.
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#


# Edit these for your printer.
tl = [0,1]            # List of tools to be compared
yc = 225              # Y line that will clear parked tools when moving in X
xz = 290              # X coord of flat plate to probe Z. 15x15mm area recommended.
yz = 285              # Y coord of flat plate to probe Z. 15x15mm area recommended. 
zo = -3.1             # Offset from flat plate area probe Z to actual Z0 on print surface.                       
# Normally, change nothing below this line.
#
#
#
toffs = [[0] * 3 for i in range(len(tl))]
import pythondcs 
import numpy as np
dcs = pythondcs.PythonDCS()

def probeTool(tn):
    dcs.resetEndstops()
    dcs.gCode('M400')
    dcs.gCode('T'+str(tn))                           # Pick up Tool 
    dcs.gCode('G10 P'+str(tn)+' Z0 X0 Y0')           # Remove all offsets from Tool 
    # Z Axis
    dcs.gCode('M574 Z1 S1 P"!io5.in"')
    dcs.gCode('G0 Z10 F1000')                        # Lower bed to avoid collision with hole plate. 
    dcs.gCode('G0 Y'+str(yc)+'              F10000') # Move nozzle to avoid other tools 
    dcs.gCode('G0 X'+str(xz)+'              F10000') # Move nozzle to axis of flat area 
    dcs.gCode('G0 X'+str(xz)+' Y'+str(yz)+' F10000') # Move nozzle to spot above flat part of plate
    dcs.gCode('G1 H3 Z1 F100')
    toffs[tn][2] = dcs.getPos()[2]                   # Capture the Z position at initial point of contact
    dcs.resetAxisLimits()
    dcs.gCode('G0 Z'+str(toffs[tn][2]+1)+' F100')       # Back off just slightly 
    dcs.gCode('G1 H3 Z1 F10')
    toffs[tn][2] = dcs.getPos()[2]                   # Capture the Z position at point of contact
    dcs.resetAxisLimits()
    dcs.gCode('G0 Z'+str(toffs[tn][2]+1)+' F100')       # Back off just slightly 
    dcs.gCode('G1 H3 Z1 F10')
    toffs[tn][2] = dcs.getPos()[2]                   # Capture the Z position at point of contact
    dcs.resetAxisLimits()
    print(toffs[tn][2])
    if (toffs[tn][2] < 1.1):
      print('Z less than 1.1, very likely miss on Z probe, stoping script to avoid damange to printer')
      dcs.resetEndstops()
      exit(8)
    dcs.gCode('G0 Z10 F1000')                      # Lower bed to avoid collision with hole plate. 
    dcs.gCode('M574 Z1 S1 P"nil"')
    
    dcs.gCode('T-1')
    dcs.gCode('M400')
# End of probeTool function

#
# Main
#
for t in tl:
    probeTool(t)
dcs.resetEndstops()

# Display Results
# Actually set G10 offsets
for i in range(len(toffs)):
    tn = tl[i]
    print('G10 P'+str(tn)+' Z'+str(np.around((-toffs[i][2])-zo,3)))
