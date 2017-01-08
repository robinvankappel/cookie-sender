import time
import urllib2
import json
import bz2
import sys
import os

##### GLOBAL VARIABLES ####
START_TIME = time.time()

def get_time():
    time_new = (time.time()-START_TIME)
    time_str = '+'+str(int(time_new/60.0))+'min (' + str(int(time_new)) + 'sec)'
    return time_str

def compress(data):
    print get_time() + ' start compressing'
    compressed_file = bz2.compress(data)
    print get_time() + ' finalised compressing'
    return compressed_file

def FileWriteIsDone(path, filesize=None, timeout=999):
    sys.stdout.write('\r'+str(timeout))
    sys.stdout.flush()
    if (timeout <= 0):
        return False
    if (os.path.isfile(path)):
        filesize_new = os.stat(path).st_size
        if (filesize_new == filesize) and (filesize > 10000):
            with open(path, 'r+') as f:
                file = f.read()
                if 'END_OF_FILE' in file:
                    f.closed
                    print get_time() + 'file succesfully read'
                    return file;
                else:
                    time.sleep(1)
                    return FileWriteIsDone(path, filesize_new, timeout - 1)
        else:
            time.sleep(1)
            return FileWriteIsDone(path, filesize_new, timeout - 1)
    else:
        time.sleep(1)
        return FileWriteIsDone(path,filesize,timeout - 1)

class Result():
    """
    Make object containing key and pio_result
    """
    def __init__(self, pio_result,key):
        self.pio_result = pio_result
        self.key = key

def log_to_file(file,log_path,response=None):
    if response.code == 201:#successfull
        success = 1
    elif response.code == 403:
        print get_time(),'Error: sent package was empty'
        success = 0
    else:
        success = 0
        print get_time(), 'Error: reponse code = ', str(response.code)
    #write to external file
    with open(log_path, 'a') as f:
        if success == 0:
            if not response == None:
                content = file + ' (failed sending to db)' + get_time() +'\n'
                content += 'response: ' + response.read() + '\n\n'
            else:
                content = file + ' (failed sending to db)' + get_time() +'\n'
        elif success == 1:
            content = file + ' (successfully sent to db)' + get_time() +'\n'
        print content
        f.write(content)
    return

