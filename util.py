import time
import bz2
import sys
import os


##### GLOBAL VARIABLES ####

def get_time():
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    time_str = ' (' + time_now + ') '
    return time_str

class Compress():
    def __init__(self,json_content):
        data = str(json_content)
        print get_time() + ' start compressing'
        self.file = bz2.compress(data)
        self.filesize = round(self.file.__sizeof__() / 1000000.0, 1)
        print get_time() + ' finalised compressing (filesize = ' + str(self.filesize) + 'MB)'

    #Wait till file is fully written. If timeout = -1, iteration never stops
def FileWriteIsDone(path, dir, filesize=None, timeout=-1):
    end = False
    no_meta_data = False
    while 1:
        sys.stdout.write('\r'+str(abs(timeout)))
        sys.stdout.flush()
        if (timeout == 0):
            if no_meta_data:# metadata still not written, thus move file.
                filepath, file = os.path.split(path)
                erroneous_folder = os.path.join(dir, 'no_meta_data-output_files')
                if not os.path.exists(erroneous_folder):
                    os.makedirs(erroneous_folder)
                print get_time() + 'no meta data found in file, moving file to other folder'
                os.rename(path, os.path.join(erroneous_folder,file))
            print get_time() + "time out has passed, file is skipped"
            return False
        if (os.path.isfile(path)):
            filesize_new = os.stat(path).st_size
            if (filesize_new == filesize) and (filesize > 10000):
                with open(path, 'r+') as f:
                    file = f.read()
                    if 'END_OF_FILE' in file:
                        end = True
                    else:#wait till metadata is written
                        no_meta_data = True
                        time.sleep(1)
                        timeout -= 1
                        filesize = filesize_new
                while end:
                    if f.closed:
                        print get_time() + 'file succesfully read'
                        return file;
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

def log_response(file, flop, stack_size, pot_type, log_path, filesize, keys_length, response=None):
    filesize_per_key = round(filesize*1024/float(keys_length),0)
    content = 'SENDER flop: ' + flop + ', ' + stack_size + 'BB, ' + pot_type + ' | file: ' + file + ', DB_filesize_total = ' + str(filesize) + 'MB, DB_filesize_per-key = ' + str(
                filesize_per_key) + 'KB |'
    #write content
    if response == None:
        content += ' FAILED: no response'
        print get_time(), 'NO RESPONSE'
        success = 0
    elif 'response.code' in locals():
        if response.code == 201:
            content += ' Successfully sent to db: response = ' + str(response.code)
            success = 1
        else:
            content += ' FAILED: wrong response from db: response = '
            success = 0
            if response == 404:
                content += str(response) + '(Http error 404: not found)'
                print get_time(), 'Http error 404: not found.'
            elif response.code == 403:
                content += str(response.code) + '(sent package was empty)'
                print get_time(), 'Error: sent package was empty'
            else:
                print get_time(), 'Error: reponse code = ', str(response.code)
                content += str(response.code)

    content += get_time() + '\n'
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

#gives back iterators; type list(split_every(a,b)) to retrieve the elements in a list
def chunkIt(seq, num):
  avg = len(seq) / float(num)
  out = []
  last = 0.0

  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg

  return out