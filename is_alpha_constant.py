"""
Tells if alpha(pixel) == const over al imahe pixels

Sintax:
    img.py filename
"""
import sys

from PIL import Image
import numpy as np

def img_info(img_path):
    im = Image.open(img_path)
    print(im)
    if im.mode == "RGBA":
        # has a constant alpha value?
        im_a = im.getchannel('A')
        data = np.asarray(im_a)
        a0 = data[0][0] 
        uf = np.vectorize(lambda a: a==a0)
        is_const = np.all(uf(data)) 
        if is_const:
            print("image has constant alpha value ==", a0)
        else:
            print("image has not a constant alpha value")

def help():
    print(__doc__)

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        cmd = help
    elif (len(sys.argv) > 2) or sys.argv[1] in ["-h", "--help"]:
        cmd = help
    else:
        img_info(sys.argv[1] )
        sys.exit(0)
    cmd()
