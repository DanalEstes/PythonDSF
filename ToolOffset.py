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
    # Z Axis
    dcs.gCode('M574 Z1 S1 P"!io4.in"')
    dcs.gCode('G0 Z10       F1000')          # Lower bed to avoid collision with square hole plate. 
    dcs.gCode('G0      Y225 F10000')        # Move nozzle to avoid other tools 
    dcs.gCode('G0 X290      F10000')        # Move nozzle to avoid other tools 
    dcs.gCode('G0 X290 Y285 F10000')   # Move nozzle to spot above flat part of plate
    dcs.gCode('G1 H3 Z1 F100')
    toolZ[tn] = dcs.getPos()[2]         # Capture the Z position at point of contact
    dcs.resetAxisLimits()
    print(toolZ[tn])
    dcs.gCode('G0 Z10 F1000')          # Lower bed to avoid collision with square hole plate. 
    dcs.gCode('M574 Z1 S1 P"nil"')
    
    # X Axis - First Pass for finding Y center
    dcs.gCode('M574 X1 S1 P"!io4.in"')
    dcs.gCode('G0 X290 Y272 F1000')        # Place the nozzle tip in center of square hole. 
    dcs.gCode('G0 Z'+str(toolZ[tn]-2)+' F100')   # Place the nozzle tip just below surface.
    dcs.gCode('M675 X R1 F100')
    toolX[tn] = dcs.getPos()[0]        # Capture the X position at point of contact
    dcs.gCode('M574 X1 S1 P"nil"')

    # Y Axis
    dcs.gCode('M574 Y1 S1 P"!io4.in"')
    dcs.gCode('M675 Y R1 F100')
    toolY[tn] = dcs.getPos()[1]        # Capture the Y position at point of contact
    dcs.gCode('M574 Y1 S1 P"nil"')

    # X Axis - Second Pass now that Y is centered
    dcs.gCode('M574 X1 S1 P"!io4.in"')
    dcs.gCode('M675 X R1 F100')
    toolX[tn] = dcs.getPos()[0]        # Capture the X position at point of contact
    dcs.gCode('M574 X1 S1 P"nil"')

toolZ = [0,0]
toolX = [0,0]
toolY = [0,0]
# Start of probing for Tool 0
dcs.resetEndstops()
dcs.gCode('T0')                   # Pick up Tool zero
dcs.gCode('G10 P0 Z0 X0 Y0')      # Remove all offsets from Tool zero
probeTool(0)
dcs.gCode('M400')
# End of probing Tool 0
dcs.gCode('T-1')
dcs.gCode('M400')
# Start of probing for Tool 1
#dcs.gCode('G0 Y200 F1000')        # avoid other tools. 
dcs.gCode('T1')                   # Pick up Tool one
dcs.gCode('G10 P1 Z0 X0 Y0')      # Remove all offsets from Tool one
probeTool(1)
# End of probing Tool 0

dcs.gCode('M400')
dcs.gCode('T-1')                  # Put down all tools

print('Tool 0 X = '+str(toolX[0])+' Tool 1 X = '+str(toolX[1])+' X difference = '+str(toolX[0]-toolX[1]))
print('Tool 0 Y = '+str(toolY[0])+' Tool 1 Y = '+str(toolY[1])+' Y difference = '+str(toolY[0]-toolY[1]))
print('Tool 0 Z = '+str(toolZ[0])+' Tool 1 Z = '+str(toolZ[1])+' Z difference = '+str(toolZ[0]-toolZ[1]))

dcs.resetEndstops()
