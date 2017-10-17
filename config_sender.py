##### SETTINGS GOOGLE INSTANCE ########
PARALLEL_PROC = True #Processing with multiple watchers
USE_CMD = False #Processing with one watcher, activated from command line: "python cookie_sendercookie_sender.py 'folder-to-watch'"

# ##### SETTINGS PC JELLE ########
# JSON_DIR = 'C:\\Users\\J. Moene\\Desktop\\CookieMonster_pythonfiles\\generated_scripts\\json_files\\temp'
# PIORESULTS_DIR = 'C:\\Users\\J. Moene\\Desktop\\CookieMonster_pythonfiles\\db-filler\\generated_scripts\\OUTPUT_results'
# WATCH_DIR = PIORESULTS_DIR

##### SERVER PARAMETERS #####
class Url_selector():
    """
    Define which urls (=end points) belong to which stack size, pot type and initial card
    INPUT VARIABLES: flop, pot type, stack size
    OUTPUT VARIABLES: Url
    """
    def __init__(self, pot_type, stack_size):
        if stack_size == '60':
            if pot_type == 's':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','http://0','http://0','http://0')
            elif pot_type == '3':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','http://0','http://0','http://0')
            elif pot_type == '4':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','http://0','http://0','http://0')
        elif stack_size == '140':
            if pot_type == 's':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','0','http://0','http://0')
            elif pot_type == '3':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','0','http://0','http://0')
            elif pot_type == '4':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','0','http://0','http://0')
            elif pot_type == '5':
                flop_picker = [['A', '2', '3', '4', '5'], ['8', 'K'], ['T', 'Q'], ['6', '7', '9', 'J']]
                urls = ('http://0','0','http://0','http://0')
        self.flop_picker = flop_picker
        self.urls = urls
        self.pot_type = pot_type
    #choose the url based on the initial flop letter
    def choose(self,flop):
        for i,v in enumerate(self.flop_picker):
            if flop[0] in v:
                url0 = self.urls[i]
                break
        if self.pot_type == 's':
            url_upload = '/insertsrp'
        elif self.pot_type == '3':
            url_upload = '/insertdriebet'
        elif self.pot_type == '4':
            url_upload = '/insertvierbet'
        elif self.pot_type == '5':
            url_upload = '/insertvijfbet'
        else:
            print 'url = None'
            return None
        return url0 + url_upload