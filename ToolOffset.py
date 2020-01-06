#!/usr/bin/env python3
# Python script intended to determine tool-to-tool offsets on a tool changing 3D printer
#   running a Duet 3 with Pi.
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
xh = 290              # X coord of hole in which nozzle is inserted to probe XY.  15mm dia recommended 
yh = 272              # Y coord of hole in which nozzle is inserted to probe XY.  15mm dia recommended 
hd = 1.1              # Depth to lower nozzle into hole when probing. Depends on shape of nozzle. 
                      # About .9 to 1.1 works for most brass nozzles. 
# Normally, change nothing below this line.
#
#
#
toffs = [[0] * 3 for i in range(len(tl))]
import pythondcs 
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
    print(toffs[tn][2])
    if (toffs[tn][2] < 1.1):
      print('Z less than 1.1, very likely miss on Z probe, stoping script to avoid damange to printer')
      dcs.resetEndstops()
    dcs.gCode('G0 Z10 F1000')                      # Lower bed to avoid collision with hole plate. 
    dcs.gCode('M574 Z1 S1 P"nil"')
    
    # X Axis - First Pass for finding Y center
    dcs.gCode('M574 X1 S1 P"!io5.in"')
    dcs.gCode('G0 X'+str(xh)+' Y'+str(yh)+' F1000')    # Place the nozzle tip in center of hole. 
    dcs.gCode('G0 Z'+str(toffs[tn][2]-1.1)+' F100')  # Place the nozzle tip just below surface.
    dcs.gCode('M675 X R1 F100')                      # Probe both ways, thus creating a chord and leaving nozzle at center X
    dcs.gCode('M574 X1 S1 P"nil"')

    # Y Axis
    dcs.gCode('M574 Y1 S1 P"!io5.in"')
    dcs.gCode('M675 Y R1 F100')        # Probe both ways for Y while centered on X... now centered on Y
    toffs[tn][1] = dcs.getPos()[1]     # Capture the Y position
    dcs.gCode('M574 Y1 S1 P"nil"')

    # X Axis - Second Pass now that Y is centered
    dcs.gCode('M574 X1 S1 P"!io5.in"')
    dcs.gCode('M675 X R1 F100')        # Probe both ways on X while centered on Y... now centered on both X and Y
    toffs[tn][0] = dcs.getPos()[0]     # Capture the X position 
    dcs.gCode('M574 X1 S1 P"nil"')

    dcs.gCode('T-1')
    dcs.gCode('M400')
# End of probeTool function

#
# Main
#
for t in tl:
    probeTool(t)

for i in range(len(toffs)):
    for j in range(len(toffs[i])): 
        print('Tool '+str(i)+' Axis '+str(j)+' = '+str(toffs[i][j])) 

for j in range(len(toffs[0])): 
    print('Axis '+str(j)+' difference = '+str(toffs[0][j]-toffs[1][j])) 


dcs.resetEndstops()

