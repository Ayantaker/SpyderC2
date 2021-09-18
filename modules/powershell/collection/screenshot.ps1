[Reflection.Assembly]::LoadWithPartialName("System.Drawing") | out-null
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

return $bytes