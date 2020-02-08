## SUMMARY

This repository contains a Python module intended to interface with the "Duet Software Framework" found on a Duet 3 controller board for 3D Printers when that board is used with a ribbon cable attached Raspberry Pi. 

## PythonDCS:

Specifically, it provides a module called pythondcs.py that contains a class of named PythonDCS. At this time, it contains methods to connect to the "Duet Control Server".  Since it connects to a priveleged socket on the Pi, it must run with root priveleges, such as "sudo". 

The methods include:

#### Gcode('cmd') 
Passes the command argument to the printer, waits for execution, and returns the response (if any). 
#### getPos()
Returns a Python list containing the current position of the machine, in MM. Normally list[0] is X, list[1] is Y, and so on. 
#### resetEndstops()
Removes the endstops on XYZU and probe K0.  Scans the 'config.g' file of the printer for all M574 and M558 commands, and executes them.  This has the net effect of setting up all endstops as though the printer 
#### resetAxisLimits()
Scans the 'config.g' file of the printer for all M208 commands, and executes them.  This is particularly useful after G1 H3 command (which resets hi axis limit). 

### ToolOffset.py

This repository also contains a sample script that is designed to measure tool-to-tool offsets on a tool changing 3D printer.  This script was specifically developed for the Jubilee printer. 

It assumes that a plate exists with known coordinates attached to the bed.  This plate has a flat area, minimum 15x15mm for touch probing Z, and contains a round hole with crisp 90 deg edges between the wall of the hold and the surface. This hole should be about 15mm in diameter. This plate must be grounded. The nozzle of each tool must be connected via a wire to io4.in on the main 6HC board. 

You will then need to edit the coordinates of the Z touch area, and the center of the hole, into the begining of the ToolOffset.py script.

The first several times you run this, be extra ready to E-Stop the printer. 

### Zonly.py

Like ToolOffset, but only does Z.  Perhaps you will use a camera for XY. 

