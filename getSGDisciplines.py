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

def getDisciplines(sg,prjName,entName,userName):
	disciplines = []

	userFilter = [['login','is',userName]]
	userData = sg.find('HumanUser',userFilter,['name'])

	filters1 = [ ['name','is',prjName]]
	project = sg.find('Project',filters1)
	prjId = project[0]['id']
	filters2 = [ ['code','is',entName]]
	order=[{'column':'content','direction':'asc'}]

	entities = sg.find('Asset',filters2)
	if len(entities)>0:
		entId = entities[0]['id']
		filters3 = [['project','is', {'type':'Project','id':prjId}],['entity', 'is', {'type':'Asset', 'id':entId}],['task_assignees','is',userData[0]]]
		tasks = sg.find('Task',filters3,['content','step'],order)

	else:
		entities = sg.find('Shot',filters2)
		entId = entities[0]['id']
		filters3 = [['project','is', {'type':'Project','id':prjId}],['entity', 'is', {'type':'Shot', 'id':entId}],['task_assignees','is',userData[0]]]
		tasks = sg.find('Task',filters3,['content','step'],order)

	print '----'
	for p in tasks:
		if disciplines.count(p['step']['name'])==0:
			disciplines.append(p['step']['name'])
			print p['step']['name']
	

# ---------------------------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------------------------
if __name__ == '__main__': 

	inParam = sys.argv[1:]
	projectName = inParam[0]
	entName = inParam[1]
	userName = inParam[2]
	SERVER_PATH = inParam[3]
	SCRIPT_NAME = inParam[4]
	SCRIPT_KEY = inParam[5]
	sg = connect()
	#newVName = getVersionNumber(sg,'monsterEvA_Model',67,'monsterEvA')
	#print newVName
	getDisciplines(sg,projectName,entName,userName)
	
