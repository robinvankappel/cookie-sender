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

def send_file(file,url_db_upload):
    url = url_db_upload
    req = urllib2.Request(url)
    #req.add_header('content-type', 'multipart/form-data')
    try:
        print get_time() + 'start sending to url'
        response = urllib2.urlopen(req, file)
    except urllib2.HTTPError as e:
        #print e.code
        #print e.read()
        print 'exit program'
        exit()
    except:
        print 'failed to send file'
        print 'exit program'
        exit(1)
    return response

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

def key2fullkey(flopname, key, pot_type, bet_size):
    full_key = flopname + '_' + str(pot_type) + '_' + str(int(bet_size * 10.0)) + '_' + key.replace(':', '_')
    return full_key

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
                content = file + ' (failed sending to db)\n'
                content += 'response: ' + response.read()
            else:
                content = file + ' (failed sending to db)\n'
        elif success == 1:
            content = file + ' (successfully sent to db)\n'
        print content
        f.write(content)
    return

