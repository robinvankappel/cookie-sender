#http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import util
import process
import json

##### GLOBAL INPUT VARIABLES ####
JSON_DIR = 'C:\\Users\\J. Moene\\Desktop\\CookieMonster_pythonfiles\\generated_scripts\\json_files\\temp'
PIORESULTS_DIR = 'C:\\Users\\J. Moene\\Desktop\\CookieMonster_pythonfiles\\db-filler\\generated_scripts\\OUTPUT_results\\'
WATCH_DIR = PIORESULTS_DIR
#SENTJSON_FOLDER = WATCH_DIR + 'sent_jsons\\'
URL_DB = 'http://5.79.86.66/app_dev.php/'
URL_DB_UPLOAD = URL_DB + 'upload'
LOG_FILE = 'log_watcher.txt'

##### GLOBAL VARIABLES (don't change) ####


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
            output = util.FileWriteIsDone(file)
            print util.get_time(),"Start processing pio results"
            if WATCH_DIR == PIORESULTS_DIR:
                #convert pio results to json content
                json_content_dict = process.create_json(output,file)
                json_content = json.dumps(json_content_dict)
            elif WATCH_DIR == JSON_DIR:

                json_content = open(file, 'rb').read()
            else:
                print 'ERROR: WATCH_DIR wrongly defined'
                exit(1)
            # compress json file and send
            compressed_file = util.compress(str(json_content))
            print 'filesize = ' + str(round(compressed_file.__sizeof__() / 1000000.0, 1)) + 'MB'
            process.send_json(compressed_file, URL_DB_UPLOAD, file, PIORESULTS_DIR, LOG_FILE)
            # remove file
            print util.get_time(),'removing file'
            os.remove(file)
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
    # use this line when you run this program from pycharm
    #observer.schedule(MyHandler(), path=WATCH_DIR, recursive=True)

    # use this line when you run this program via cmd:
    # #arg in cmd: python main.py 'dir to watch'
    # e.g. dir to watch = C:/Users/J." "Moene/Desktop/CookieMonster_pythonfiles/db-filler/generated_scripts/OUTPUT_results/
    observer.schedule(MyHandler(), path=args[0] if args else '.', recursive=True)

    observer.start()
    print 'watcher started'

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
