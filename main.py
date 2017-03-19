#http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import util
import process
import json

##### LOCAL PATHS #####
from config_paths import *

##### ADDITIONAL PARAMETERS #####
LOG_FILE = 'log_watcher.txt'

class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.txt"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print util.get_time(),event.src_path, event.event_type   # print now only for debug

    # def on_modified(self, event):
    #     self.process(event)
    #     self.on_finished(event)

    def on_created(self, event):
        self.process(event)
        self.on_finished(event.src_path)

    def on_finished(self,file):
        print 'Waiting till file write is finished...'
        try:
            output = util.FileWriteIsDone(file,PIORESULTS_DIR,timeout=120)
            if not output:
                return
            util.log_outputfiles(file, os.path.join(PIORESULTS_DIR, LOG_FILE))
            print util.get_time(),"Start processing pio results"
            if WATCH_DIR == PIORESULTS_DIR:
                #convert pio results to json content
                flop, json_content_dict, pot_type, keys_length = process.create_json(output,file)
                if not 'URL_PICKER' in globals():
                    global URL_PICKER
                    URL_PICKER = process.url_picker(URLS_DB)
                url_db = process.choose_url(flop,URL_PICKER)
                print util.get_time() + " pot type = " + pot_type
                json_content = json.dumps(json_content_dict)
            elif WATCH_DIR == JSON_DIR:
                json_content = open(file, 'rb').read()
            else:
                print 'ERROR: WATCH_DIR wrongly defined'
                exit(1)
            # compress json file and send
            compressed_file = util.compress(str(json_content))
            filesize = round(compressed_file.__sizeof__() / 1000000.0, 1)
            print 'filesize = ' + str(filesize) + 'MB'
            response = process.send_json(compressed_file, url_db, pot_type)
            success = util.log_response(file, os.path.join(PIORESULTS_DIR,LOG_FILE), filesize, keys_length, pot_type, response)
            if success == 1:
                # remove file
                print util.get_time(),'removing file'
                if os.path.isfile(file):
                    os.remove(file)
                else:
                    print 'ERROR: Removal of file was not possible, since it cannot be found'
        except:
            'Failed to process flop'

#in cmd: python main.py path_to_watch
if __name__ == "__main__":
    ###
    args = sys.argv[1:]
    if not os.path.exists(WATCH_DIR):
        print 'wrong path definition'
        exit(1)
    observer = Observer()

    # 1. use this line when you run this program from pycharm
    #observer.schedule(MyHandler(), path=WATCH_DIR, recursive=True)

    # 2. use this line when you run this program via cmd: (alternatively run a batch file which activates multiple watchers)
    ###arg in cmd: python main.py 'dir to watch'
    ###e.g. dir to watch = C:/Users/J." "Moene/Desktop/CookieMonster_pythonfiles/db-filler/generated_scripts/OUTPUT_results/A
    observer.schedule(MyHandler(), path=args[0] if args else '.', recursive=True)

    observer.start()
    print 'watcher started'

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
