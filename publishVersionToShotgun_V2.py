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
        print "Connecting to %s..." % (SERVER_PATH),
        sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
        print "connected"
        return sg
    except Exception, e:
        print "Unable to connect to Shotgun server. "+str(e)
        exit(0)

def source2path(source):
	import re
	sourceArray = re.split('\.',source)
	pathArray = re.split('/',sourceArray[0])
	filenameLength = len(pathArray[len(pathArray)-1])
	path = sourceArray[0][:-filenameLength]
	return path

def findProjectIdByName(projectName):
	filters = [ ['name','is',projectName],]
	project = sg.find('Project',filters)
	return project[0]['id']

def findUserIdByName(userName):
	filters = [ ['login','is',userName],]
	user = sg.find('HumanUser',filters)
	return user[0]['id']

def generateQuicktime(sourcePath,quick,slateData,ff,lf):
	from subprocess import call
	import re
	import os
	sourceCmd = ''
	targetCmd = ''

	targetCmd = "%s.mov" % quick

#defining slate data
	slateName = slateData[0]
	slateProject = "Project=%s" %slateData[1]
	slateEntity = "Entity=%s" %slateData[2]
	slateDiscipline = "Discipline=%s" %slateData[3]
	slateTask = "Task=%s" %slateData[4]
	if slateData[5]!="":
		slateDescription = "Description=%s" %slateData[5]
	else:
		slateDescription = "Description=---"
	slateUser = "User=%s" %slateData[6]

	overlayText = "testing"

	fullCmd = "/software/RV/bin/rvio %s -leader simpleslate %s %s %s %s %s %s %s -o %s -outres 1280 720 -t %s-%s" %(quick,slateName,slateProject,slateEntity,slateDiscipline,slateTask,slateDescription,slateUser,targetCmd,ff,lf)
	print "\n ------------------------------\n"
	print fullCmd
	os.system(fullCmd)
	return targetCmd

def getAssetVersionNumbered(sg,versionName,pjId,link):
	import re
	count = 0
	countStr = ""
	filters = [ ['project','is', {'type':'Project','id':pjId}],['entity', 'is', {'type':'Asset', 'id':link[0]['id']}] ]
	version = sg.find('Version',filters,['code'])

	for ver in version:
		if(re.match(versionName,ver['code'])):
			count=count+1
	count=count+1
	if count>99:
		countStr = str(count)
	else:
		if count>9:
			countStr = "0"+str(count)
		else:
			countStr = "00"+str(count)
	newVersionName = versionName+"_V"+countStr
	return newVersionName

def getShotVersionNumbered(sg,versionName,pjId,link):
	import re
	count = 0
	countStr = ""
	filters = [ ['project','is', {'type':'Project','id':pjId}],['entity', 'is', {'type':'Shot', 'id':link[0]['id']}] ]
	version = sg.find('Version',filters,['code'])

	for ver in version:
		if(re.match(versionName,ver['code'])):
			count=count+1
	count=count+1
	if count>99:
		countStr = str(count)
	else:
		if count>9:
			countStr = "0"+str(count)
		else:
			countStr = "00"+str(count)
	newVersionName = versionName+"_V"+countStr
	return newVersionName

def generateThumbnail(source,frame):
	from subprocess import call
	import re
	import os
	thumbStatus1 = 'creating thumbnail'
	thumbStatus2 = 'thumbnail created'
	padSplit = ''
	sourceCmd = ''
	targetCmd = ''

	sourceArray2 = re.split('\.',source)
	padding1Count=source.count('#');
	padding2Count=source.count('@');
	if padding1Count>0:
		for i in range(1,padding1Count):
			padSplit=padSplit+'#'
	if padding2Count>0:
		for i in range(1,padding2Count):
			padSplit=padSplit+'@'
	if padding1Count>0 or padding2Count>0:
		sourceArray1 = re.split(padSplit,source)
		sourceCmd = "%s.%s%s%s" %(sourceArray2[0],frame,padSplit,sourceArray1[1])
	else:
		sourceCmd = source
	
	targetCmd = "%s_thumbnail_.jpg" %(sourceArray2[0])
	fullCmd = "/software/RV/bin/rvio %s -o %s -outres 200 200" %(sourceCmd,targetCmd)
	os.system(fullCmd)
	return targetCmd

def updateShotByCode(sg,code, link, disc, descr, tags, quick):
	
	import re
	tagsArray = re.split(',',tags)
	filters = [ ['code','is',code], ]
	shot = sg.find('Shot',filters)
	data = { 'description': descr, 'tag_list': tagsArray}
	sg.update('Shot', shot[0]['id'], data)

def encode(source):
	source = urllib.quote(source)
	newSource = ''
	for char in source:
		if char=="/":
			newSource=newSource+'%2f';
		else:
			newSource=newSource+char;
	return newSource

def createShotVersion(sg,project,link,disc,taskName,descr,tags,user,source,frame,quick, ff, lf):
	import re
	sourceArray = re.split('\.',source)
	framesPath = source2path(source)
	print framesPath

	tagsArray = re.split(',',tags)
	versionName = "%s_%s" %(link,disc)
	QTlink = ''
	encodedSource=encode(source);
	RVlink = 'rvlink://%20-l%20-play%20'+encodedSource;


	thumb = "%s_Thumbnail.jpg" %(quick)

	pjId = findProjectIdByName(project)
	userId = findUserIdByName(user)

	filters = [ ['project','is', {'type':'Project','id':pjId}],['code', 'is', link] ]
	shot = sg.find('Shot',filters)

	filters = [ ['project','is', {'type':'Project','id':pjId}],['entity','is',{'type':'Shot','id':shot[0]['id']}],['content', 'is', taskName]]
	tasks = sg.find('Task',filters)

	versionName = getShotVersionNumbered(sg,versionName,pjId,shot)

	data = { 'project': {'type':'Project','id':pjId},
           'code': versionName,
           'description': descr,
           'sg_path_to_frames': framesPath,
           'sg_status_list': 'rev',
           'entity': {'type':'Shot', 'id':shot[0]['id']},
           'tag_list': tagsArray,
           'sg_task': {'type':'Task', 'id':tasks[0]['id']},
           'sg_rv_link': {'url':RVlink,'name':'view in RV'},
	       'user': {'type':'HumanUser', 'id':userId} }
	result = sg.create('Version', data)
	versionID = result['id']
	sg.upload_thumbnail("Version", versionID, thumb)

	if quick!='':
		QTlink = generateQuicktime(framesPath,quick,[versionName,project,link,disc,taskName,descr,user],ff,lf)
		result = sg.upload("Version",versionID,QTlink,"sg_qt",versionName)

def createAssetVersion(sg,project,link,disc,taskName,descr,tags,user,source,frame,quick, ff, lf):
	import re
	sourceArray = re.split('\.',source)
	framesPath = source2path(source)
	print framesPath

	tagsArray = re.split(',',tags)
	versionName = "%s_%s" %(link,disc)
	QTlink = ''
	encodedSource=encode(source);
	RVlink = 'rvlink://%20-l%20-play%20'+encodedSource;


	thumb = "%s_Thumbnail.jpg" %(quick)

	pjId = findProjectIdByName(project)
	userId = findUserIdByName(user)

	filters = [ ['project','is', {'type':'Project','id':pjId}],['code', 'is', link] ]
	asset = sg.find('Asset',filters)

	filters = [ ['project','is', {'type':'Project','id':pjId}],['entity','is',{'type':'Asset','id':asset[0]['id']}],['content', 'is', taskName]]
	tasks = sg.find('Task',filters)

	versionName = getAssetVersionNumbered(sg,versionName,pjId,asset)

	data = { 'project': {'type':'Project','id':pjId},
           'code': versionName,
           'description': descr,
           'sg_path_to_frames': framesPath,
           'sg_status_list': 'rev',
           'entity': {'type':'Asset', 'id':asset[0]['id']},
           'tag_list': tagsArray,
           'sg_task': {'type':'Task', 'id':tasks[0]['id']},
           'sg_rv_link': {'url':RVlink,'name':'view in RV'},
	       'user': {'type':'HumanUser', 'id':userId} }
	result = sg.create('Version', data)
	versionID = result['id']
	sg.upload_thumbnail("Version", versionID, thumb)

	if quick!='':
		QTlink = generateQuicktime(framesPath,quick,[versionName,project,link,disc,taskName,descr,user],ff,lf)
		result = sg.upload("Version",versionID,QTlink,"sg_qt",versionName)



# ---------------------------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------------------------
if __name__ == '__main__':    

	letters = 'p:j:l:c:k:s:d:t:u:s:f:q:w:x:v:b:n:'
	keywords = ['type=','project=','link=','discipline=','task=','description=', 'tags=','user=','source=','frame=','quicktime=','firstFrame=','lastFrame=','scriptUrl=','scriptName=','scriptKey=']
	opts, extraparams = getopt.getopt(sys.argv[1:],letters)

	vType=''
	project=''
	link=''
	discipline=''
	task=''
	description=''
	tags=''
	user=''
	source=''
	frame='1'
	quick=''
	firstFrame=''
	lastFrame=''

	for o,p in opts:
		if o in ['-p','--type']:
			vType = p
		if o in ['-j','--project']:
			project = p
		if o in ['-l','--link']:
			link = p
		if o in ['-c','--discipline']:
			discipline = p
		if o in ['-k','--task']:
			task = p
		if o in ['-d','--description']:
			description = p
		if o in ['-t','--tags']:
			tags += p
		if o in ['-u','--user']:
			user = p
		if o in ['-s','--source']:
			source = p
		if o in ['-f','--frame']:
			frame = p
		if o in ['-q','--quicktime']:
			quick = p
		if o in ['-w','--firstFrame']:
			firstFrame = p
		if o in ['-x','--lastFrame']:
			lastFrame = p
		if o in ['-v','--scriptUrl']:
			SERVER_PATH = p
		if o in ['-b','--scriptName']:
			SCRIPT_NAME = p
		if o in ['-n','--scriptKey']:
			SCRIPT_KEY = p

	print SERVER_PATH
	print SCRIPT_NAME
	print SCRIPT_KEY

	sg = connect()
	if vType=='shot':
		createShotVersion(sg, project, link, discipline, task, description, tags, user, source, frame, quick, firstFrame, lastFrame)
	if vType=='asset':
		createAssetVersion(sg, project, link, discipline, task, description, tags, user, source, frame, quick, firstFrame, lastFrame)
