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
            output = util.FileWriteIsDone(file,WATCH_DIR,timeout=120)
            if not output:
                return
            util.log_outputfiles(file, os.path.join(WATCH_DIR, LOG_FILE))
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
            success = util.log_response(file, os.path.join(WATCH_DIR,LOG_FILE), compressed_file.filesize, keys_length, pot_type, response)#todo: evaluate
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
            arg in cmd: python main.py 'dir to watch'
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
        # Using Pool:
        pool = mp.Pool(processes=WATCHERS)
        # TODO: REWRITE THIS FUNCTION BASED ON WATCHERS CLASS (containing all info)
        var1 = 'D:\\db-filler\\generated_scripts\\OUTPUT_results\\A'
        var2 = 'D:\\db-filler\\generated_scripts\\OUTPUT_results\\B'
        var3 = 'D:\\db-filler\\generated_scripts\\OUTPUT_results\\C'
        # init_program(path_app,global_vars_1)#test function

        print 'Starting async process 1'
        one = pool.apply_async(Watcher, args=(False,var1))
        time.sleep(1)
        print 'Starting async process 2'
        two = pool.apply_async(Watcher, args=(False,var2))
        time.sleep(1)
        print 'Starting async process 3'
        three = pool.apply_async(Watcher, args=(False, var3))

        one.get()
        two.get()
        three.get()

        pool.close()
        pool.join()
    else:
        #if run from command line; argument is recursive folder
        watcher = Watcher(cmd=USE_CMD)#recursive, uses argument





