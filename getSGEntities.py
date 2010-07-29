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

def getEntities(sg,prjName,userName):

	filteredAssets = []
	filteredShots = []
	userFilter = [['login','is',userName]]
	userData = sg.find('HumanUser',userFilter,['name'])

	filters1 = [ ['name','is',prjName]]
	project = sg.find('Project',filters1)
	prjId = project[0]['id']
	filters2 = [ ['project','is', {'type':'Project','id':prjId}]]
	order=[{'column':'code','direction':'asc'}]
	assets = sg.find('Asset',filters2,['code'],order)
	shots = sg.find('Shot',filters2,['code'],order)

	filters3 = [ ['project','is', {'type':'Project','id':prjId}],['task_assignees','is',userData[0]]]
	tasks = sg.find('Task',filters3,['entity'],order)

	#now let's filter by users, looking for each asset's tasks
	for asset in assets:
		for task in tasks:
			if task['entity']['name']==asset['code']:
				filteredAssets.append(asset['code'])
	
	#now let's filter by users, looking for each shot's tasks
	for shot in shots:
		for task in tasks:
			if task['entity']['name']==shot['code']:
				filteredShots.append(shot['code'])

	print '----'
	print len(filteredAssets)
	for p in filteredAssets:
		print p

	print '-----------SHOTS-------------------\n'
	for p in filteredShots:
		print p

# ---------------------------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------------------------
if __name__ == '__main__': 

	inParam = sys.argv[1:]
	projectName = inParam[0]
	userName = inParam[1]
	SERVER_PATH = inParam[2]
	SCRIPT_NAME = inParam[3]
	SCRIPT_KEY = inParam[4]
	sg = connect()
	#newVName = getVersionNumber(sg,'monsterEvA_Model',67,'monsterEvA')
	#print newVName
	getEntities(sg,projectName,userName)
	
