
import OpenEXR
import numpy as np

def exr_to_array(exrfile):
    file = OpenEXR.InputFile(exrfile)
    dw = file.header()['dataWindow']

    channels = file.header()['channels'].keys()
    channels_list = list()
    for c in ('R', 'G', 'B', 'A'):
        if c in channels:
            channels_list.append(c)

    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    color_channels = file.channels(channels_list)
    channels_tuple = [np.fromstring(channel, dtype='f') for channel in color_channels]
    res = np.dstack(channels_tuple)
    return res.reshape(size + (len(channels_tuple),))