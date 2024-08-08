#import torch
#import ollama
import os
#from openai import OpenAI
#import argparse
import re
import json

file_path = "good-TR-JSON.txt"
inputfile_for_localAI = "input_for_localAI.txt"
ericsson_terms_file = 'ericsson-terms-remove.txt'
final_json_out = []


if file_path:
    with open(file_path, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)
        with open(inputfile_for_localAI, "w+") as outfile:
       

            for i in data['issues']:
                #print(json.dumps(i['key'],i['fields']['summary']))
                #print(i['key'],i['fields']['summary'])
                # what keys & corresponding field names are H/C below

                """    
                "AI_input_fields": [
                "key": "key",
                "summary":"['fields']['summary']",
                "Issue Description" : "['fields']['customfield_25119']",
                "Impact": "['fields']['customfield_30068']",
                "Resolution Details" : "['fields']['customfield_39227']"
                ] """

                ### REMOVE E// data before write !! 
                ###
                with open(ericsson_terms_file, 'r') as erc_file:
                    line = erc_file.readline()
                    while line:
                        #print("e// term = "+line)
                        # the re.IGNORECASE is used to ignore cases
                        compileObj = re.compile(re.escape(line.strip()), re.IGNORECASE)
                        #Substitute the substring with replacing a string using the regex sub() function

                        #Replace in all fields
                        i['key'] = compileObj.sub('', i['key'])
                        i['fields']['summary'] = compileObj.sub('', i['fields']['summary'])
                        i['fields']['customfield_25119'] = compileObj.sub('', i['fields']['customfield_25119'])
                        i['fields']['customfield_30068'] = compileObj.sub('', i['fields']['customfield_30068'])
                        if i['fields']['customfield_39227']: 
                            i['fields']['customfield_39227'] = compileObj.sub('', i['fields']['customfield_39227'])
                        #i['key'] = i['key'].replace(line.strip(),'')
                        line = erc_file.readline()
                #print("updated key= "+i['key'])
                ###

                outjson = {}
                outjson['key'] = i['key']
                outjson['summary'] = i['fields']['summary']
                outjson['Issue Description'] = i['fields']['customfield_25119']
                outjson['Impact'] = i['fields']['customfield_30068']
                outjson['Resolution Details'] = i['fields']['customfield_39227']
                #check if "fields" are read fine 
                print("wrote key ="+outjson['key'])


                final_json_out.append(outjson)

            json.dump(final_json_out, outfile)


