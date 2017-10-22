import urllib2
import util
import os
##### LOCAL PATHS #####
from config_sender import *

def create_json(output, file):
    json_content = dict()
    stack_size = os.path.basename(file)[0:2]
    pot_type = os.path.basename(file)[3:4]
    flop = os.path.basename(file)[5:11]
    # get results, keys and metadata from file
    print util.get_time(), "get results, keys and metadata from file"
    pio_results, keys, bet_size = splitfile(output)
    # check whether number of keys and results are equal
    if (len(keys) == len(pio_results)) == False:
        print 'ERROR: number of found keys in Pio results file is not equal to keys (requires debugging)'
        exit(1)
    # make object of result-key combination
    results = list()
    print util.get_time(), "make object of result-key combination"
    for i, pio_result in enumerate(pio_results):
        key = keys[i]
        results.append(util.Result(pio_result, key))
    # process results per key
    print util.get_time(), "process results per key..."
    keys_list = list()
    for result in results:
        result_per_hand = result.pio_result.split('\n')
        # get json content
        json_content_of_key = get_json_from_result(result_per_hand)
        # generate full key
        DB_key = key2DBkey(flop, result.key)
        # add to json
        json_content[DB_key] = json_content_of_key

        # key size check:
        keys_list.append(DB_key)
    avg_keylength, max_keylength = averageLen(keys_list)
    print util.get_time(), 'Avg key length: ' + str(avg_keylength)
    print util.get_time(), "json_content generated"
    return flop, json_content, pot_type, stack_size, len(keys)


def averageLen(lst):
    lengths = [len(i) for i in lst]
    max_length = max(lengths)
    if not('MAX_LENGTH_TILL_NOW' in globals()):
        global MAX_LENGTH_TILL_NOW
        MAX_LENGTH_TILL_NOW = 0
    if max_length > MAX_LENGTH_TILL_NOW:
        print util.get_time() + 'Max key length: ' + str(max_length) + " --> key: " + str(lst[lengths.index(max_length)])
        MAX_LENGTH_TILL_NOW = max_length
    if len(lengths) == 0:
        avg_length = 0
    else:
        avg_length = (float(sum(lengths)) / len(lengths))
    return avg_length, max_length


def get_json_from_result(result_per_hand):
    # find lines with children and extract action
    actions, end_of_file_index = get_actions_and_end_of_file(result_per_hand)
    # make json content and add to dict
    json_content_of_key = build_json(result_per_hand, actions, end_of_file_index)
    # compress:
    # json_content_of_key = bz2.compress(json_content_of_key)
    return json_content_of_key


def get_actions_and_end_of_file(file):
    actions = list()
    already_detected = 0
    for i, line in enumerate(file):
        # get actions and bet sizes
        if "child " in line:
            next_line = file[i + 1]
            next_line_split = next_line.split(':')
            # if c is not after a bet, it must be a check
            last_element = next_line_split[-1]
            if last_element == 'c' and not next_line_split[-2].startswith('b'):
                actions.append('x')  # k = check
            elif last_element == 'c':
                actions.append('c')  # c = check
            elif last_element.startswith('b'):
                actions.append(last_element[1:])  # only bet size, without the b
            elif last_element == 'f':
                actions.append(last_element)  # f = fold
            else:
                'unrecognised element as action in children'
                exit()
        # get first END word to get part of file with results
        elif line == 'END' and already_detected == 0:
            end_of_file_index = i - 1
            already_detected = 1
    return actions, end_of_file_index


def build_json(file, actions, end_of_file_index):
    # get results between first line and empty line
    file_results = file[1:end_of_file_index - 2]
    json_content_of_key = {}
    json_content_of_key.update({'sizings': actions})
    for i, line in enumerate(file_results):
        hand = line.split(':')[0]
        line2 = filter(None, line.split(' '))[1:]
        values = [int(round(float(x) * 100)) for x in line2]
        json_content_of_key.update({str(hand): values})
    return json_content_of_key


def splitfile(file):
    file = file.replace('stdoutredi ok!', '')
    splitfile = file.split("END_OF_RESULTS")
    if len(splitfile) != 2:
        print "ERROR: 'END_OF_RESULTS' not found in output file > cannot process the file"
    pio_results = splitfile[0].split("is_ready ok!")[:-1]
    keys = splitfile[1] \
               .split('KEYS_START')[1] \
               .split('KEYS_END')[0] \
               .split("\n")[1:-1]
    pot_type = splitfile[1] \
                   .split('POT_TYPE')[1] \
                   .split('BET_SIZE')[0] \
                   .split("\n")[1:-1][0]  # not used, read from file name
    bet_size = splitfile[1] \
                   .split('BET_SIZE')[1] \
                   .split("\n")[1:-1][0]
    return pio_results, keys, float(bet_size)


def send_json(json_content, url):
    if url is None:
        print util.get_time(), 'ERROR: pot type not recognised, cannot upload to DB.'
        return None
    req = urllib2.Request(url)
    req.add_header('content-type', 'application/json')
    # JSON_CHUNKS = 1000
    try:
        # for k, v in islice(json_content.iteritems(), JSON_CHUNKS):
        print util.get_time(), 'start sending to DB...'
        response = urllib2.urlopen(req, json_content)
    except urllib2.HTTPError as e:
        print e.code
        print e.read()
        print util.get_time() + ' send json FAILED'
        response = e.code
    except:
        print util.get_time() + ' send json FAILED'
        response = None
    return response

def key2DBkey(flopname, key):
    key = key.replace('b', '')
    key = key.replace('r:0:', '')
    key = key.replace(':', '_')
    full_key = flopname + key
    return full_key

def choose_url(flop, pot_type, stack_size):
    if not ('URL_SELECTOR') in globals():
        global URL_SELECTOR
        URL_SELECTOR = Url_selector(pot_type, stack_size)
    url = URL_SELECTOR.choose(flop)
    return url
