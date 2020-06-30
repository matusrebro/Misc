"""

Script downloads Contents file from:
http://ftp.uk.debian.org/debian/dists/stable/main/Contents
for user defined architecture and lists top ten packages

Parameters
----------
architecture : TYPE string
    architecture name, for example amd64

Returns
-------
None.

"""

import sys
from urllib import request
import gzip
from io import StringIO
import pandas as pd

def download_contents(architecture):
    """
    Function downloads a .gz Contents file for a architecture
    and returns the contents as a binary

    Parameters
    ----------
    architecture : string
        architecture name, for example amd64

    Returns
    -------
    file_content : bytes
        binary contents of a Content file

    """
    content_url = 'http://ftp.uk.debian.org/debian/dists/stable/main/Contents-'+architecture+'.gz'
    with request.urlopen(content_url) as response:
        with gzip.GzipFile(fileobj=response) as uncompressed:
            file_content = uncompressed.read()
    return file_content


def get_top_ten_packages(architecture):
    """

    Parameters
    ----------
    architecture : string
        architecture name, for example amd64

    Returns
    -------
    None.

    """
    file_content = download_contents(architecture)
    data = StringIO(str(file_content, 'utf-8'))
    _df = pd.read_csv(data, names=['filename', 'packages'],
                      engine='python',
                      delimiter=r"\s(?=\S*$)")
    _df = _df.drop('filename', 1)
    _df = (_df.set_index(['packages'])
           .apply(lambda x: x.str.split(',').explode())
           .reset_index())
    _df = _df.groupby(['packages']).size().reset_index(name='counts')
    index_stop = min((_df.shape[0], 10))
    index = 0
    for _, row in _df.sort_values(by=['counts'], ascending=False)[:index_stop].iterrows():
        print(str(index+1) + '. ' + row['packages'] + ' ' + str(row['counts']))
        index += 1

if __name__ == '__main__':
    get_top_ten_packages(sys.argv[1])
    