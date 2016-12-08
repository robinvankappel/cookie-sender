import urllib2
import json
import util
import os

def create_json(pio_results_file):
    json_content = dict()
    flop = os.path.basename(pio_results_file)[0:5]
    with open(pio_results_file,'r+') as f:
        #todo: read line by line and save to python object
        print util.get_time(),'reading pio results file'
        file = f.readlines()
        #get results, keys and metadata from file
        print util.get_time(),"get results, keys and metadata from file"
        pio_results,keys,pot_type,bet_size = splitfile(file)
        # check whether number of keys and results are equal
        if (len(keys) == len(pio_results)) == False:
            print 'ERROR: number of found keys in Pio results file is not equal to keys (requires debugging)'
            exit(1)
        #make object of result-key combination
        results = list()
        print util.get_time(), "make object of result-key combination"
        for i,pio_result in enumerate(pio_results):
            key = keys[i]
            results.append(util.Result(pio_result,key))
        # process results per key
        print util.get_time(), "process results per key..."
        for result in results:
            result_per_hand = result.pio_result.split('\n')
            #get json content
            json_content_of_key = get_json_from_result(result_per_hand)
            # generate full key
            full_key_corr = util.key2fullkey(flop, result.key, pot_type, bet_size)
            #add to json
            json_content[full_key_corr] = json_content_of_key
    f.closed
    print util.get_time(), "json_content generated"
    return json_content

def get_json_from_result(result_per_hand):
    #find lines with children and extract action
    actions, end_of_file_index = get_actions_and_end_of_file(result_per_hand)
    # make json content and add to dict
    json_content_of_key = build_json(result_per_hand, actions, end_of_file_index)
    # compress:
    # json_content_of_key = bz2.compress(json_content_of_key)
    return json_content_of_key

def get_actions_and_end_of_file(file):
    actions = list()
    already_detected = 0
    for i,line in enumerate(file):
        #get actions and bet sizes
        if "child " in line:
            next_line = file[i+1]
            next_line_split = next_line.split(':')
            #if c is not after a bet, it must be a check
            last_element = next_line_split[-1]
            if last_element == 'c' and not next_line_split[-2].startswith('b'):
                actions.append('x')#k = check
            elif last_element == 'c':
                actions.append('c')#c = check
            elif last_element.startswith('b'):
                actions.append(last_element[1:])#only bet size, without the b
            elif last_element == 'f':
                actions.append(last_element)#f = fold
            else:
                'unrecognised element as action in children'
                exit()
        #get first END word to get part of file with results
        elif line == 'END' and already_detected == 0:
            end_of_file_index = i-1
            already_detected = 1
    return actions, end_of_file_index

def build_json(file,actions,end_of_file_index):
    # get results between first line and empty line
    file_results = file[1:end_of_file_index-2]
    json_content_of_key = {}
    json_content_of_key.update({'sizings':actions})
    for i,line in enumerate(file_results):
        hand = line.split(':')[0]
        line2 = filter(None,line.split(' '))[1:]
        values = [int(round(float(x)*100)) for x in line2]
        json_content_of_key.update({str(hand):values})
    return json_content_of_key

def splitfile(file):
    splitfile = file.split("free_tree ok!")
    #todo: not present anymore in result file, use other identifier.
    pio_results = splitfile[0].split("stdoutredi_append ok!")[1:]
    keys = splitfile[1] \
               .split('KEYS START')[1] \
               .split('KEYS END')[0] \
               .split("\n")[1:-1]
    pot_type = splitfile[1] \
                   .split('POT_TYPE')[1] \
                   .split('BET_SIZE')[0] \
                   .split("\n")[1:-1][0]
    bet_size = splitfile[1] \
                   .split('BET_SIZE')[1] \
                   .split("\n")[1:-1][0]
    return pio_results,keys,pot_type,float(bet_size)