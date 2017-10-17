#http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
import time
import sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import util
import process
import json
sys.path.append('D:\cookie')
##### LOCAL PATHS #####
from config_sender import *
from config_cookie import *


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
            output = util.FileWriteIsDone(file,WATCH_DIR,timeout=120)
            if not output:
                return
            #util.log_outputfiles(file, os.path.join(WATCH_DIR, LOG_FILE))#todo: remove if not used in log
            print util.get_time(),"Start processing pio results"

            #convert pio results to json content
            flop, json_content_dict, pot_type, stack_size, keys_length = process.create_json(output,file)
            url = process.choose_url(flop, pot_type, stack_size)
            print util.get_time() + " flop = " + flop + " | pot type = " + pot_type + \
                  " | stack size = " + stack_size + " | url = " + url
            json_content = json.dumps(json_content_dict)

            # compress json file and send
            compressed_file = util.Compress(json_content)
            #compressed_file = util.compress(str(json_content))
            response = process.send_json(compressed_file, url)
            success = util.log_response(file, flop, stack_size, pot_type, LOG_FILE, compressed_file.filesize, keys_length, response)#todo: evaluate output
            success = 1 #todo: temp for testing...
            if success == 1:
                # remove file
                print util.get_time(),'removing file'
                if os.path.isfile(file):
                    os.remove(file)
                else:
                    print 'ERROR: Removal of file was not possible, since it cannot be found'
        except:
            'Failed to process flop'

class Watcher():
    def __init__(self,cmd=True,watch_dir=WATCH_DIR):
        """
        If cmd = False:
            use this when you run this program from pycharm
        If cmd = True:
            use this when you run this program via cmd: (alternatively run a batch file which activates multiple watchers)
            arg in cmd: python cookie_sendercookie_sender.py 'dir to watch'
            e.g. dir to watch = C:/Users/J." "Moene/Desktop/CookieMonster_pythonfiles/db-filler/generated_scripts/OUTPUT_results/A
        """
        if not os.path.exists(watch_dir):
            print 'wrong path definition'
            exit(1)
        observer = Observer()

        if cmd==False:
            observer.schedule(MyHandler(), path=watch_dir, recursive=True)
        else:
            args = sys.argv[1:]
            observer.schedule(MyHandler(), path=args[0] if args else '.', recursive=True)

        observer.start()
        print 'watcher started'
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    if PARALLEL_PROC:
        import multiprocessing as mp
        ##Multiprocessing: Process / Pool / Thread.
        watchers = Watchers(WATCHERS,WATCH_DIR)
        # Using Pool:
        pool = mp.Pool(processes=watchers.number)
        processes = list()
        for i, folder in enumerate(watchers.paths):
            print 'Starting async process ' + str(i+1)
            p = pool.apply_async(Watcher, args=(False, folder))
            processes.append(p)
            time.sleep(0.1)
        for p in processes:
            p.get()
        pool.close()
        pool.join()
    else:
        #if run from command line; argument is recursive folder
        watcher = Watcher(cmd=USE_CMD)#recursive, uses argument





