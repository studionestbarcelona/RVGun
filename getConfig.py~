import os
import sys
import getopt

inParam = sys.argv[1:]
cfgFile = inParam[0]

data = ["","","",""]

if os.path.exists(cfgFile):
	f = open(cfgFile, 'r')
	lines = f.readlines()
	for l in lines:
		if(l[0]!="#"):
			partitions = l.rpartition('=')
			if partitions[0]=="rvgun_temp":
				data[0]=partitions[2][0:len(partitions[2])-1]
			elif partitions[0]=="sgScript_server_path":
				data[1]=partitions[2][0:len(partitions[2])-1]
			elif partitions[0]=="sgScript_name":
				data[2]=partitions[2][0:len(partitions[2])-1]
			elif partitions[0]=="sgScript_key":
				data[3]=partitions[2][0:len(partitions[2])-1]
print ""
print data[0]
print data[1]
print data[2]
print data[3]
