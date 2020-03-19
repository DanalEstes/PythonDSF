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
xz = 288              # X coord of tool nozzle over flat plate to probe Z. 15x15mm area recommended.
yz = 285              # Y coord of tool nozzle over flat plate to probe Z. 15x15mm area recommended.
xp = 260              # X coord of BLtouch over flat plate to probe Z. 15x15mm area recommended.
yp = 340              # Y coord of BLtouch over flat plate to probe Z. 15x15mm area recommended.
# Normally, change nothing below this line.
#
#
#
toffs = [[0] * 3 for i in range(len(tl))]
poffs = 0
import pythondcs 
import numpy as np
dcs = pythondcs.PythonDCS()

def probePlate():
    dcs.resetEndstops()
    dcs.resetAxisLimits()
    dcs.gCode('T-1')
    dcs.gCode('M280 P0 S160')
    dcs.gCode('G32 G28 Z')
    dcs.gCode('G0 Z10 F1000')                        # Lower bed to avoid collision with hole plate. 
    dcs.gCode('G0 Y'+str(yc)+'              F10000') # Move carriage to avoid other tools 
    dcs.gCode('G0 X'+str(xp)+'              F10000') # Move BLt to axis of flat area 
    dcs.gCode('G0 X'+str(xp)+' Y'+str(yp)+' F10000') # Move BLt to spot above flat part of plate
    dcs.gCode('G30 S-1')                             # Probe plate with BLt
    global poffs
    poffs = dcs.getPos()[2]                          # Capture the Z position at initial point of contact
    print("Plate Offset = "+str(poffs))
    dcs.gCode('G0 Z10 F1000')                        # Lower bed to avoid collision with hole plate. 


def probeTool(tn):
    dcs.resetEndstops()
    dcs.resetAxisLimits()
    dcs.gCode('M400')
    dcs.gCode('M280 P0 S160')
    dcs.gCode('G28 Z')
    dcs.gCode('G10 P'+str(tn)+' Z0')           # Remove z offsets from Tool 
    dcs.gCode('T'+str(tn))                           # Pick up Tool 
    # Z Axis
    dcs.gCode('M558 K0 P9 C"nil"')
    dcs.gCode('M574 Z1 S1 P"!io5.in"')
    dcs.gCode('G0 Z10 F1000')                        # Lower bed to avoid collision with hole plate. 
    dcs.gCode('G0 Y'+str(yc)+'              F10000') # Move nozzle to avoid other tools 
    dcs.gCode('G0 X'+str(xz)+'              F10000') # Move nozzle to axis of flat area 
    dcs.gCode('G0 X'+str(xz)+' Y'+str(yz)+' F10000') # Move nozzle to spot above flat part of plate
    dcs.gCode('G1 H3 Z-4 F10')
    print("Tool Offset for tool "+str(tn)+" first pass is "+str(dcs.getPos()[2]))
    dcs.resetAxisLimits()
    dcs.gCode('G0 Z4 F100')                          # Lower bed for second pass
    dcs.gCode('G1 H3 Z-4 F10')
    toffs[tn][2] = dcs.getPos()[2]                   # Capture the Z position at initial point of contact
    dcs.resetAxisLimits()
    print("Tool Offset for tool "+str(tn)+" is "+str(toffs[tn][2]))
    dcs.gCode('G0 Z10 F1000')                      # Lower bed to avoid collision with hole plate. 
    dcs.gCode('M574 Z1 S1 P"nil"')
    dcs.resetEndstops()
    dcs.resetAxisLimits()
    dcs.gCode('T-1')
    dcs.gCode('M400')
# End of probeTool function

#
# Main
#
probePlate()
for t in tl:
    probeTool(t)
dcs.resetAxisLimits()
dcs.resetEndstops()

# Display Results
# Actually set G10 offsets
print("Plate Offset = "+str(poffs))
for i in range(len(toffs)):
    tn = tl[i]
    print("Tool Offset for tool "+str(tn)+" is "+str(toffs[tn][2]))
    print('G10 P'+str(tn)+' Z'+str(np.around((poffs-toffs[i][2]),2)))
