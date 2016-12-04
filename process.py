import urllib2
import json

# def create_json(pio_results_file):
#     json_content = dict()
#     with open(pio_results_file,'r+') as f:
#         file = f.read()
#         results_per_key = file.split("stdoutredi_append ok!")
#         results_per_key = results_per_key[1:] #skip first line
#         if (len(subkeys) == len(results_per_key)) == False:
#             print 'ERROR: number of found keys in Pio results file is not equal to keys (requires debugging)'
#         for i,result in enumerate(results_per_key):
#             subkey = subkeys[i]
#             split_file = result.split('\n')
#             #find lines with children and extract action
#             actions,index = util.get_actions_and_end_of_file(split_file)
#             # generate full key
#             full_key_corr = util.key2fullkey(flop, subkey, POT_TYPE, BET_SIZE)
#             #make json content and add to dict
#             json_content_of_key = util.build_json(split_file,actions,index)
#             json_content[full_key_corr] = json_content_of_key
#     f.closed
#     return json_content
