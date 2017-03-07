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

def log_response(file,log_path, filesize, keys_length, pot_type, response=None):
    filesize_per_key = round(filesize*1024/float(keys_length),0)
    content = file
    #write content
    if response.code == 201:#successfull
        success = 1
        content += ' (successfully sent to db[' + str(pot_type) + ']: response = 201'
        content += ', DB_filesize_total = ' + str(filesize) + 'MB, DB_filesize_per-key = ' + str(
            filesize_per_key) + 'KB'
    elif response == 404:
        print get_time(), 'Http error 404: not found.'
        success = 0
    elif response == None:
        print get_time(), 'Http error 404: not found.'
        success = 0
    else:
        success = 0
        content += ' (failed sending to db[' + str(pot_type) + ']:'
        if response.code == 403:
            print get_time(),'Error: sent package was empty'
            content += 'response = ' + str(response.code)
        elif response == 404:
            print get_time(), 'Http error 404: not found.'
            content += 'response = ' + str(response)
        elif response == None:
            print get_time(), 'No response'
            content += 'no response'
        else:
            print get_time(), 'Error: reponse code = ', str(response.code)
            content += 'response = ' + str(response.code)
    content += ')' + get_time() + '\n'
    #write to external file
    with open(log_path, 'a') as f:
        print get_time(), 'logging: ' + content
        f.write(content)
    return success

def log_outputfiles(file, log_path):
    # write to external file
    with open(log_path, 'a') as f:
        content = file + ' (fully written to disk)' + get_time() + '\n'
        f.write(content)
    return