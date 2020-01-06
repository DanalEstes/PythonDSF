# Python module intended for interface to the Duet Software Framework
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT 
#
# As of Jan 2020, functions for interacting with Duet Control Server are implemented,
#  plus a few things specific to the virtual SD config.g
#

import socket
import json

class PythonDCS:
        
    def openDCS(self):
        self.DCSsock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.DCSsock.connect('/var/run/dsf/dcs.sock')
        self.DCSsock.setblocking(True)
        j=json.dumps({"mode":"command"}).encode()
        self.DCSsock.send(j)
        r=self.DCSsock.recv(128).decode()
        if (-1 == r.find('{"version":')):
              print("Failed to enter command mode - version not received")
              print(r)
              exit(8)
        if (-1 == r.find('{"success":true}')):   #could be in same buffer as version
            r=self.DCSsock.recv(128).decode()
            if (-1 == r.find('{"success":true}')):
                  print("Failed to enter command mode - success not received")
                  print(r)
                  exit(8)

    def closeDCS(self):
        self.DCSsock.close()

    def gCode(self,cmd=''):
        print(cmd)
        j=json.dumps({"code": cmd,"channel": 0,"command": "SimpleCode"}).encode()
        self.DCSsock.send(j)
        r=self.DCSsock.recv(2048).decode()
        if ('Error' in r):
          print('Error detected, stopping script')
          print(j)
          print(r)
          exit(8)
        return(r)

    def getPos(self):
      result = json.loads(self.gCode('M408'))['result']
      pos = json.loads(result)['pos']
      print('getPos = '+str(pos))
      return pos

    def resetEndstops(self):
      self.gCode('M574 X1 S1 P"nil"')
      self.gCode('M574 Y1 S1 P"nil"')
      self.gCode('M574 Z1 S1 P"nil"')
      self.gCode('M574 U1 S1 P"nil"')
      self.gCode('M558 K0 P5 C"nil"')  
      c = open('/opt/dsf/sd/sys/config.g','r')
      for each in [line for line in c if 'M574' in line]: self.gCode(each)
      c.close()    
      c = open('/opt/dsf/sd/sys/config.g','r')
      for each in [line for line in c if 'M558' in line]: self.gCode(each)
      c.close()    


    def resetAxisLimits(self):
      c = open('/opt/dsf/sd/sys/config.g','r')
      for each in [line for line in c if 'M208' in line]: self.gCode(each)
      c.close()    

    def __init__(self):
      self.openDCS()

    def __enter__(self):
      return self

    def __exit__(self, *args):
      self.closeDCS()

