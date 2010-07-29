module: RVGun {
use math;
use math_util;
use rvui;
use rvtypes;
use app_utils;
use extra_commands;
use commands;
use qt;
use gl;
use glu;
use external_qprocess;
require glyph;
require io;

class: TestMinorMode : MinorMode
{
	string            _machine;
	string            _user;
	bool              _leaveUiVisible;
	bool              _topLevel;
	QColorDialog      _colorDialog;

	QDockWidget       _publishDock;
	QWidget           _publishPane;
	QToolButton       _publishButton;
	QToolButton       _cancelButton;
	QComboBox		  _projectCombo;
	QComboBox		  _linkCombo;
	QComboBox		  _disciplineCombo;
	QComboBox		  _taskCombo;
	QLineEdit		  _descriptionLineEdit;
	QLineEdit		  _tagsLineEdit;
	QCheckBox		  _quicktimeCheck;
	int               _dockArea;
	QAction			  _publishAction;
	QAction			  _cancelAction;
	QAction			  _projectAction;
	QInputDialog      _justTest;

	string			  _testTextValue;
	string 			  pythonCallParam;

	int				  assetsNumber;


	//configuration variables
	string rvgun_temp;				//temporary folder for thumbnail and quicktime generation
	string sgScript_url;			//shotgun script data: path to shotgun server, name of shotgun script, key of shotgun script
	string sgScript_name;
	string sgScript_key;
	

	method: auxFilePath (string; string icon)
    {
        io.path.join(supportPath("RVGun", "RVGun.zip"), icon);
    }

    method: auxIcon (QIcon; string name)
    {
        QIcon(auxFilePath(name));
    }

	method: getConfig(void;)
	{
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
		
		let extProc = ExternalQProcess("python","python",[auxFilePath("getConfig.py"),auxFilePath("rvgun.cfg")], time, tipo,cleanFn);
		string output = extProc._outList;
		string[] data = output.split("\n");
		rvgun_temp = data[1];
		sgScript_url = data[2];
		sgScript_name = data[3];
		sgScript_key = data[4];
	}

	method: checkType(string; int entListId) //checks whether an entity from the list is an asset or a shot
	{
		string result = "";
		if(entListId<=assetsNumber)
		{
			result = "asset";
		}
		else
		{
			result = "shot";
		}
		return result;
	}


	method: buildTags(string; string def,string disc,string tags) //takes all the tags introduced by the user and concate them with the default ones
	{
		string result="%s,%s" % (def,disc);
		if(tags!="")
		{
			result = "%s,%s" % (result,tags);
		}	
		while(result[result.size()-1]==",")
		{
			result=result.substr(0,result.size()-1);
		}
		return result;
	}

	method: getGlobalMedia(string; string workDir,string source) //gets the global path to the current media in rv
	{
		string outPath;
		if(source.substr(0,1)!="/")
		{
			outPath = "%s/%s" % (workDir,source);
		}
		else
		{
			outPath = source;
		}
		return(outPath);
	}

	method: publish(void; bool checked, string user) //performs the publishing onto Shotgun
	{
		use io;
		use rvtypes.ExternalProcess.Type;
		require system;
		
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
		
		//check if temporary folder exists and, if not, create it
		string cmd = auxFilePath("make_RVGun_Temp_Folder.py");
		let extProc = ExternalQProcess("python","python", [cmd], time, tipo,cleanFn);

		let tempFolder = rvgun_temp;
		string[] sessionChunks =sessionFileName().split("/");
		

		//declaring and initializing some variables
		string defaultTag="internal";
		string project="";
		string val1="";
		string val2="";
		string val3="";
		string val4="";
		string taskVal="";
		string vType="";
		string quicktime="0";
		
		//getting values from UI
		project=_projectCombo.currentText();
		val1=(_linkCombo.currentText());
		val2=(_disciplineCombo.currentText());
		val3=(_descriptionLineEdit.displayText());
		val4=(_tagsLineEdit.displayText());
		taskVal=(_taskCombo.currentText());

		val4 = buildTags(defaultTag,val2,val4); //building the tag list, including the default tags, the discipline and user tags
	

		string media = sourceMedia("source000")._0; //getting the source name from RV
		string mediaInfo = getCurrentAttributes(); //getting some info about the source from RV
		let cwd = system.getcwd(); //getting the working path
		string globalMedia = getGlobalMedia(cwd,media); //generating the full path to the media

		vType = checkType(_linkCombo.currentIndex());
		print("\n");

		let (text, ok) = QInputDialog.getText(mainWindowWidget(), 
                                              "Confirmation",
                                              "Do you want to procede?(yes/no):",
                                              QLineEdit.Normal,
                                              "",
                                              Qt.Dialog);
        if (ok && text=="yes")
		{
			print("yes");
			string firstFrame = "%d"% frameStart(); //getting first frame of the sequence
			string lastFrame = "%d"% frameEnd(); //getting last frame of the sequence
			string strText = text;

			//now print out some console information
			print("\ntype: ");
			print(vType);
			print("\nproject: ");
			print(project);
			print("\nlink: ");
			print(val1);
			print("\ndiscipline: ");
			print(val2);
			print("\ntask: ");
			print(taskVal);
			print("\ndescription: ");
			print(val3);
			print("\ntags: ");
			print(val4);
			print("\nuser: ");
			print(user);
			print("\ntype: ");
			print(vType);
			print("\nsource: ");
			print(globalMedia);
			int currentFrame = commands.frame();
			string currentFrameStr = "%d" % currentFrame;
			print("\nframe: ");
			print(currentFrameStr);
			print("\nfirst frame: ");
			print(firstFrame);
			print("\nlast frame: ");
			print(lastFrame);
			print("\nLaunching python script\n");

			// ideally here we should check for images resolution

			//and do the work

			string sessionName = "%s.rv"%val1;
			string sessionFullFilename = "%s/%s" %(tempFolder,sessionName);
			string thumbFilename = "%s_Thumbnail.jpg" % sessionFullFilename;

			//save the session temporarly
			saveSession(sessionFullFilename);

			//generate the thumbnail
			exportCurrentFrame(thumbFilename);

			let extProc = ExternalQProcess("python","python",[auxFilePath("publishVersionToShotgun_V2.py"),"-p",vType,"-j",project,"-l",val1,"-c",val2,"-k",taskVal,"-d",val3,"-t",val4,"-u",user,"-s",globalMedia,"-f",currentFrameStr,"-q",sessionFullFilename,"-w", firstFrame, "-x", lastFrame, "-v", sgScript_url, "-b", sgScript_name, "-n", sgScript_key], time, tipo,cleanFn);
			
			//once finished, tell the user and remove temporary files
			if(extProc.isFinished())
			{
				print("\nPublish to Shotgun Completed");
				print("\n");
				process("rm",[sessionFullFilename],int64.max);
			}
		}
	}

	method: cancelFn(void; bool checked, string value)
	{
		deactivate();
	}

	method: cleanFn(void;)
	{
		print("cleaning");
	}

	method: getSGProjects(string[];string user) //gathers all user-assigned projects from Shotgun and builds a list
    {
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
let extProc = ExternalQProcess("python","python",[auxFilePath("getSGProjects.py"),user,sgScript_url,sgScript_name,sgScript_key], time, tipo,cleanFn);
		if(extProc.isFinished())
		{
			print("\nProject list imported");
		}
		string[] prjList = extProc._outList.split("\n");
		return(prjList);
    }

	method: getSGEntities(void;int prjIndex, string user) //gathers all user-assigned entities from Shotgun for a given project and builds a list
	{
		string[] entAdded;
		string projectName = _projectCombo.currentText();
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
		let extProc = ExternalQProcess("python","python",[auxFilePath("getSGEntities.py"),projectName,user,sgScript_url,sgScript_name,sgScript_key], time, tipo,cleanFn);
		if(extProc.isFinished())
		{
			print("\nEntity list imported");
		}
		string[] entityList = extProc._outList.split("\n");

		QVariant userData;
		userData = QVariant();
		_linkCombo.clear();
		_disciplineCombo.clear();
		_taskCombo.clear();
		_linkCombo.addItem("-----------ASSETS------------------",userData);
		for_index(idx; entityList)
		{
			if(idx>1)
			{
				int find = 0;
				for_index(entIdx; entAdded)
				{
					if(entAdded[entIdx]==entityList[idx])
					{
						find=find+1;
					}
				}
				if(find==0)
				{
					_linkCombo.addItem(entityList[idx],userData);
					entAdded.push_back(entityList[idx]);
				}
			}
		}
		assetsNumber = int(entityList[1]); //get the number of assets, in order to lately discriminate between assets and shots from the list
	}

	method: getSGDisciplines(void;int linkIndex, string user) //gathers all user-assigned disciplines from Shotgun for a given entity and builds a list
	{
		string projectName = _projectCombo.currentText();
		string linkName = _linkCombo.currentText();
		string[] discList;
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
		let extProc = ExternalQProcess("python","python",[auxFilePath("getSGDisciplines.py"),projectName,linkName,user,sgScript_url,sgScript_name,sgScript_key], time, tipo,cleanFn);
		if(extProc.isFinished())
		{
			print("\nDiscipline list imported");
		}
		if(extProc._outList neq nil)
		{
			discList = extProc._outList.split("\n");
		}

		QVariant userData;
		userData = QVariant();
		_disciplineCombo.clear();
		_disciplineCombo.addItem("-----------CHOOSE------------------",userData);
		for_index(idx; discList)
		{
			if(idx>0)
				_disciplineCombo.addItem(discList[idx],userData);
		}
		_taskCombo.clear();
	}

	method: getSGTasks(void;int discIndex, string user) //gathers all user-assigned tasks from Shotgun for a given discipline and builds a list
	{
		string projectName = _projectCombo.currentText();
		string linkName = _linkCombo.currentText();
		string discName = _disciplineCombo.currentText();
		string[] taskList;
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;
		let extProc = ExternalQProcess("python","python",[auxFilePath("getSGTasks.py"),projectName,linkName,discName,user,sgScript_url,sgScript_name,sgScript_key], time, tipo,cleanFn);
		if(extProc.isFinished())
		{
			print("\nTask list imported");
		}
		if(extProc._outList neq nil)
		{
			taskList = extProc._outList.split("\n");
		}

		QVariant userData;
		userData = QVariant();
		_taskCombo.clear();
		_taskCombo.addItem("-----------CHOOSE------------------",userData);
		for_index(idx; taskList)
		{
			if(idx>0)			
				_taskCombo.addItem(taskList[idx],userData);
		}	
	}

	method: get_SG_SYS_User(string;string sysUser)
	{
		use rvtypes.ExternalProcess.Type;
		rvtypes.ExternalProcess.Type tipo = ReadWrite;
		int64 time = int64.max;

		string sgUser = "";
		string data;
		
		let extProc = ExternalQProcess("python","python",[auxFilePath("read_usersmap.py"),auxFilePath("users.txt"),sysUser], time, tipo,cleanFn);
		data=extProc._outList.split("\n")[1]; //getting second line of process results
		if(data != "None")
		{
			sgUser = data; //if there is some kind of mapping for the current system user, then return the shotgun user
		}
		else
		{
			sgUser=sysUser; //if there is no mapping then try to use the system user as shotgun user
		}
		return sgUser;
	}

	method: TestMinorMode (TestMinorMode;)
	{
		use system;

		getConfig();

        _machine           = "computer";
        let _user 		   = getenv("USER","");
		_user  = get_SG_SYS_User(_user);
		
        _leaveUiVisible    = false;
		_topLevel 		   = true;

        let m = mainWindowWidget(),
            g = QActionGroup(m);	
		print("\n user: ");
		print (_user);
		print("\n");

        _publishDock   = QDockWidget("RVGun - %s"%_user, m, if _topLevel then Qt.Tool else Qt.Widget);
        _publishPane   = loadUIFile(auxFilePath("RVGun.ui"), m);

        _publishDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea);
		
		_projectCombo = _publishPane.findChild("projectList");
		_linkCombo = _publishPane.findChild("linkList");
		_disciplineCombo = _publishPane.findChild("disciplineList");
		_taskCombo = _publishPane.findChild("taskList");
		_descriptionLineEdit = _publishPane.findChild("descriptionText");
		_tagsLineEdit = _publishPane.findChild("tagsText");
        _publishButton = _publishPane.findChild("publishButton");
		_cancelButton = _publishPane.findChild("cancelButton");

		//filling project list and setting action-----------------------------------------------------------------------------------

		string[] projects = getSGProjects(_user);
		QVariant userData;
		userData = QVariant();
		_projectCombo.addItem("------CHOOSE PROJECT------------",userData);
		for_index(idx; projects)
		{
			if(idx>0)
				_projectCombo.addItem(projects[idx],userData);
		}
		connect(_projectCombo,QComboBox.activated, getSGEntities(,_user));


		//setting action for link list---------------------------------------------------------------------------------------------
		connect(_linkCombo,QComboBox.activated, getSGDisciplines(,_user));

		//setting action for discipline list---------------------------------------------------------------------------------------------
		connect(_disciplineCombo,QComboBox.activated, getSGTasks(,_user));
		

		//setting buttons action---------------------------------------------------------------------------------------------------

		//_quicktimeCheck = _publishPane.findChild("quicktimeCheck");

		_publishAction = g.addAction(auxIcon("SGUpload.png"), "Publish");
		_publishAction.setCheckable(false);
		connect(_publishAction, QAction.triggered, publish(,_user));
		_publishButton.setDefaultAction(_publishAction);

		_cancelAction = g.addAction("Cancel");
		_cancelAction.setCheckable(false);
		connect(_cancelAction, QAction.triggered, cancelFn(,"testString"));
		_cancelButton.setDefaultAction(_cancelAction);

        _publishDock.setWidget(_publishPane);
        _publishDock.ensurePolished();
        _publishDock.setGeometry(QRect(m.x() + 20,
                                    m.y() + 20,
                                    600,
                                    400));

        _publishDock.show();

        //  Call mode init
		this.init("RVGun",nil,nil);
		m.show();
	}

	method: deactivate (void;)
    {
        if (!_leaveUiVisible)
        {
            if (_publishDock neq nil) 
			{
				_publishPane.close();
				_publishDock.close();
			}
        }
    }

    method: activate (void;)
    {
        if (_publishDock neq nil) 
		{
			_publishPane.show();
			_publishDock.show();
		}
    }
}


\: createMode(Mode; )
{
    return TestMinorMode();
}

}
