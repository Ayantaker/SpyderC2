def execute_command():
	import platform
	import os
	import pdb
	import re
	import json
	if platform.system() == 'Windows':
		history_file = os.path.join(os.environ['systemdrive'], "\\Users", os.environ['username'] , "AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
		bookmark_file = os.path.join(os.environ['systemdrive'], "\\Users", os.environ['username'] , "AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks")

		history = []
		if os.path.isfile(history_file):
			f = open(history_file, "r", errors='ignore')
			f = f.read()
			
			for url in  re.findall(r'(htt(p|ps)://([\w-]+\.)+\w*)',f):
				history.append(url[0])

			history = (list(set(history)))
			formatted_output = "Browser User DataType Data \n------- ---- -------- ---- \n"
			for string in history:
				formatted_history = "Chrome  "+os.environ['username']+" History "+string+" \n"
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

			formatted_output += "Browser User DataType Data \n------- ---- -------- ---- \n"
			for string in history:
				formatted_bookmark = "Chrome  "+os.environ['username']+" Bookmark "+string+" \n"
				formatted_output+= formatted_bookmark
		else:
			return("Bookmark File not present")

		return formatted_output
		

	elif platform.system() == 'Linux':
		pdb.set_trace()