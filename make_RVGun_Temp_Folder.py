import os
import sys

newDir = os.environ.get("RVGUN_TEMP")
if(os.path.isdir(newDir)==False):
	os.mkdir(newDir)
