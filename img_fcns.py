"""
Here are some image transformation functions
"""

import numpy as np
from PIL import Image, ImageDraw

# function converts image to black and white
# and creates image with hexadecimal representation
# of the image
def img2numbers(imgName,fraction=1):
    im_frame = Image.open(imgName).convert('L') # Black and White
    newwidth=int(im_frame.size[0]/fraction)
    wpercent = (newwidth/float(im_frame.size[0]))
    hsize = int((float(im_frame.size[1])*float(wpercent)))
    im_frame = im_frame.resize((newwidth,hsize), Image.ANTIALIAS)
    np_frame = np.array(im_frame)
    color = 'rgb(255, 255, 255)' 
    sx=13
    sy=10
    newIm = Image.new('L', (np_frame.shape[1]*sx, np_frame.shape[0]*sy))
    draw = ImageDraw.Draw(newIm)
    for k in range(np_frame.shape[0]):
        for j in range(np_frame.shape[1]):
            draw.text((j*sx,k*sy),hex(np_frame[k,j]).split('x')[-1],fill=color)

    newIm.save('img_hex.jpg')
