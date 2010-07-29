import os
import sys
import getopt

inParam = sys.argv[1:]
mapFile = inParam[0]
sysUser = inParam[1]

sgUser = None

if os.path.exists(mapFile):
	f = open(mapFile, 'r')
	users = f.readlines()
	for u in users:
		if(u[0]!="#"):
			partitions = u.rpartition('=')
			if partitions[0]==sysUser:
				sgUser=partitions[2]
				break
print ""
print sgUser
