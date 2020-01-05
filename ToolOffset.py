#!/usr/bin/env python3
# Python script intended to determine tool-to-tool offsets on a tool changing 3D printer
#   running a Duet 3 with Pi.
#
# Must run with root priviledge, such as via sudo.
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#
import pythondcs 
dcs = pythondcs.PythonDCS()

def probeTool(tn):
    dcs.resetEndstops()
    dcs.gCode('M400')
    dcs.gCode('T'+str(tn))                       # Pick up Tool 
    dcs.gCode('G10 P'+str(tn)+' Z0 X0 Y0')       # Remove all offsets from Tool 
    # Z Axis
    dcs.gCode('M574 Z1 S1 P"!io5.in"')
    dcs.gCode('G0 Z10       F1000')         # Lower bed to avoid collision with hole plate. 
    dcs.gCode('G0      Y225 F10000')        # Move nozzle to avoid other tools 
    dcs.gCode('G0 X290      F10000')        # Move nozzle to avoid other tools 
    dcs.gCode('G0 X290 Y285 F10000')        # Move nozzle to spot above flat part of plate
    dcs.gCode('G1 H3 Z1 F100')
    toolZ[tn] = dcs.getPos()[2]             # Capture the Z position at initial point of contact
    dcs.resetAxisLimits()
    dcs.gCode('G0 Z'+str(toolZ[tn]+1)+' F100')   # Back off just slightly 
    dcs.gCode('G1 H3 Z1 F10')
    toolZ[tn] = dcs.getPos()[2]             # Capture the Z position at point of contact
    dcs.resetAxisLimits()
    print(toolZ[tn])
    if (toolZ[tn] < 1.1):
      print('Z less than 1.1, very likely miss on Z probe, stoping script to avoid damange to printer')
      dcs.resetEndstops()
    dcs.gCode('G0 Z10       F1000')         # Lower bed to avoid collision with hole plate. 
    dcs.gCode('M574 Z1 S1 P"nil"')
    
    # X Axis - First Pass for finding Y center
    dcs.gCode('M574 X1 S1 P"!io5.in"')
    dcs.gCode('G0 X290 Y272 F1000')        # Place the nozzle tip in center of hole. 
    dcs.gCode('G0 Z'+str(toolZ[tn]-1.3)+' F100')   # Place the nozzle tip just below surface.
    dcs.gCode('M675 X R1 F100')        # Probe both ways, thus creating a chord and leaving nozzle at center X
    dcs.gCode('M574 X1 S1 P"nil"')

    # Y Axis
    dcs.gCode('M574 Y1 S1 P"!io5.in"')
    dcs.gCode('M675 Y R1 F100')        # Probe both ways for Y while centered on X... now centered on Y
    toolY[tn] = dcs.getPos()[1]        # Capture the Y position
    dcs.gCode('M574 Y1 S1 P"nil"')

    # X Axis - Second Pass now that Y is centered
    dcs.gCode('M574 X1 S1 P"!io5.in"')
    dcs.gCode('M675 X R1 F100')        # Probe both ways on X while centered on Y... now centered on both X and Y
    toolX[tn] = dcs.getPos()[0]        # Capture the X position 
    dcs.gCode('M574 X1 S1 P"nil"')

    dcs.gCode('T-1')
    dcs.gCode('M400')
# End of proeTool function



# Main
toolZ = [0,0]
toolX = [0,0]
toolY = [0,0]
probeTool(0)
probeTool(1)
# End of probing Tool 0

dcs.gCode('M400')
dcs.gCode('T-1')                  # Put down all tools

print('Tool 0 X = '+str(toolX[0])+' Tool 1 X = '+str(toolX[1])+' X difference = '+str(toolX[0]-toolX[1]))
print('Tool 0 Y = '+str(toolY[0])+' Tool 1 Y = '+str(toolY[1])+' Y difference = '+str(toolY[0]-toolY[1]))
print('Tool 0 Z = '+str(toolZ[0])+' Tool 1 Z = '+str(toolZ[1])+' Z difference = '+str(toolZ[0]-toolZ[1]))

dcs.resetEndstops()
