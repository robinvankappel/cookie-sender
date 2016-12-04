import time
import urllib2
import json
import bz2

##### GLOBAL VARIABLES ####
START_TIME = time.time()

def get_time():
    time_new = int((time.time()-START_TIME)/60.0)
    time_str = '+'+str(time_new)+'min '
    return time_str

def send_file(file,url_db_upload):
    url = url_db_upload
    req = urllib2.Request(url)
    #req.add_header('content-type', 'multipart/form-data')
    try:
        print 'filesize = ' + str(file.__sizeof__() / 1000000) + 'MB'
        print 'start sending to url'
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

def compress(source_file):
    print 'start compressing'
    compressed_file = bz2.compress(open(source_file, 'rb').read())
    print get_time() + 'finalised compressing'
    return compressed_file

def send_json(json_content,url_db):
    url = url_db + 'upload'
    req = urllib2.Request(url)
    req.add_header('content-type', 'application/json')
    #JSON_CHUNKS = 1000
    json_dump = json.dumps(json_content)
    try:
        #for k, v in islice(json_content.iteritems(), JSON_CHUNKS):
        response = urllib2.urlopen(req, json_dump)
    except urllib2.HTTPError as e:
        print e.code
        print e.read()
    except:
        print 'send json failed'
        exit(1)
    return response
