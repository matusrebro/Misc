"""
Here are some image transformation functions
"""

import numpy as np
from PIL import Image, ImageDraw
import argparse
import sys

parser = argparse.ArgumentParser()


parser.add_argument('input_img', type=str,
                    help='name of the image file to transform')

parser.add_argument('--output_img', type=str, nargs='?', default = 'result.jpg',
                    help='name of transformed image (output) file (default: result.jpg)')

parser.add_argument('--fraction', type=int, nargs='?', default = 1,
                    help='size fraction of original image, eg. 2 meaning half of the original (default: 1)')

args = parser.parse_args()



def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush() 

"""
function converts image to black and white
and creates image with hexadecimal representation of the image
"""
def img2numbers(input_img, output_img = 'result.jpg', fraction = 1):
    im_frame = Image.open(input_img).convert('L') # Black and White
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
        progress(k+1, np_frame.shape[0], suffix='')
        
    newIm.save(output_img)


if __name__ == '__main__':
    img2numbers(args.input_img, args.output_img, args.fraction)
    

