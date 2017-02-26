import time
import bz2
import sys
import os

##### GLOBAL VARIABLES ####

def get_time():
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    time_str = ' (Time: ' + time_now + ') '
    return time_str

def compress(data):
    print get_time() + ' start compressing'
    compressed_file = bz2.compress(data)
    print get_time() + ' finalised compressing'
    return compressed_file

#Wait till file is fully written. If timeout = -1, iteration never stops
def FileWriteIsDone(path, filesize=None, timeout=-1):
    while 1:
        sys.stdout.write('\r'+str(abs(timeout)))
        sys.stdout.flush()
        if (timeout == 0):
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
                        timeout -= 1
                        filesize = filesize_new
            else:
                time.sleep(1)
                timeout -= 1
                filesize = filesize_new
        else:
            time.sleep(1)
            timeout -= 1

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
    else:
        if response.code == 403:
            print get_time(),'Error: sent package was empty'
        else:
            print get_time(), 'Error: reponse code = ', str(response.code)
        success = 0
        response_content = response.read()
    #write to external file
    with open(log_path, 'a') as f:
        if success == 0:
            if not response == None:
                content = file + ' (failed sending to db: response = ' + str(response.code) + ')' + get_time() + '\n'
            else:
                content = file + ' (failed sending to db: no response)' + get_time() +'\n'
        elif success == 1:
            content = file + ' (successfully sent to db: response = 201)' + get_time() +'\n'
        print get_time(), 'logging: ' + content
        f.write(content)
    return success

def log_outputfiles(file, log_path):
    # write to external file
    with open(log_path, 'a') as f:
        content = file + ' (fully written to disk)' + get_time() + '\n'
        f.write(content)
    return