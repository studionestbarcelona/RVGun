#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------
from shotgun_api3_preview import Shotgun
from pprint import pprint # useful for debugging
import sys
import getopt
import urllib;

# ---------------------------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------------------------
SERVER_PATH = '' # make sure to change this to https if your studio uses it.
SCRIPT_NAME = ''
SCRIPT_KEY = ''

# ---------------------------------------------------------------------------------------------
# Methods 
# ---------------------------------------------------------------------------------------------
def connect():
    try:
        sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
        return sg
    except Exception, e:
        print "Unable to connect to Shotgun server. "+str(e)
        exit(0)

def getProjects(sg,userName):
	userFilter = [['login','is',userName]]
	userData = sg.find('HumanUser',userFilter,['name'])

	prjFilter =  [['users','is',userData[0]]]
	prjs = sg.find('Project',prjFilter,['name'],order=[{'column':'name','direction':'asc'}] )
	print "---"
	for p in prjs:
		print p['name']


# ---------------------------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------------------------
if __name__ == '__main__': 

	inParam = sys.argv[1:]
	userName = inParam[0]
	SERVER_PATH = inParam[1]
	SCRIPT_NAME = inParam[2]
	SCRIPT_KEY = inParam[3]
	sg = connect()
	#newVName = getVersionNumber(sg,'monsterEvA_Model',67,'monsterEvA')
	#print newVName
	getProjects(sg,userName)
	
