#http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import util
import process

##### GLOBAL VARIABLES ####
WATCH_DIR = 'C:\\Users\\J. Moene\\Desktop\\CookieMonster_pythonfiles\\generated_scripts\\json_files\\temp'
SENTJSON_FOLDER = WATCH_DIR + 'sent_jsons\\'
URL_DB = 'http://5.79.87.151/app_dev.php/'
URL_DB_UPLOAD = URL_DB + 'upload'

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

        #send the json file
        #json_content = process.create_json(event.src_path)
        compressed_file = util.compress(event.src_path)
        util.send_file(compressed_file,URL_DB_UPLOAD)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

#in cmd: python main.py path_to_watch
if __name__ == "__main__":
    args = sys.argv[1:]
    if not os.path.exists(WATCH_DIR):
        print 'wrong path definition'
    observer = Observer()
    observer.schedule(MyHandler(), path=WATCH_DIR, recursive=True)
    observer.start()
    print 'watcher started'

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
