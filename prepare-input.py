#import torch
#import ollama
import os
#from openai import OpenAI
#import argparse
import re
import json

#file_path = "good-TR-JSON.txt"
file_path = "pilotTRsDump.json"
inputfile_for_localAI = "input_for_localAI.json"
ericsson_terms_file = 'ericsson-terms-remove.txt'
final_json_out = []
final_json_key_val = {}


if file_path:
    with open(file_path, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)
        with open(inputfile_for_localAI, "w+") as outfile:
       

            for i in data['issues']:
                #print(json.dumps(i['key'],i['fields']['summary']))
                #print(i['key'],i['fields']['summary'])
                # what keys & corresponding field names are H/C below

                """    
                "Issue-id": "key",
                "summary":"['fields']['summary']",
                "Issue Description" : "['fields']['customfield_25119']",
                "Impact": "['fields']['customfield_30068']",
                "Resolution Details" : "['fields']['customfield_39227']"
                Test phase (.val): 19973
                SHBF(P) (.val): 48911
                SHBF(T)(.val): 48912
                Reason for slippage (.val): 48913
                ] """

                if i['key']:
                  print("processing : ",i['key'],"..")

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
                        if i['fields']['summary'] :
                            i['fields']['summary'] = compileObj.sub('', i['fields']['summary'])
                        if i['fields']['customfield_25119'] :
                            i['fields']['customfield_25119'] = compileObj.sub('', i['fields']['customfield_25119'])
                        if i['fields']['customfield_30068'] :
                            i['fields']['customfield_30068'] = compileObj.sub('', i['fields']['customfield_30068'])
                        if i['fields']['customfield_39227']: 
                            i['fields']['customfield_39227'] = compileObj.sub('', i['fields']['customfield_39227'])
                            #Test phase
                        if i['fields']['customfield_19973'] :
                          if i['fields']['customfield_19973']['value'] :
                            i['fields']['customfield_19973']['value'] = compileObj.sub('', i['fields']['customfield_19973']['value'])
                            #shbf-p
                        if i['fields']['customfield_48911'] :
                          if i['fields']['customfield_48911']['value'] :
                            i['fields']['customfield_48911']['value'] = compileObj.sub('', i['fields']['customfield_48911']['value'])
                            #shbf-t
                        if i['fields']['customfield_48912'] :
                          if i['fields']['customfield_48912']['value'] :
                            i['fields']['customfield_48912']['value'] = compileObj.sub('', i['fields']['customfield_48912']['value'])
                            #RFS
                        if i['fields']['customfield_48913'] :
                          if i['fields']['customfield_48913']['value'] :
                            i['fields']['customfield_48913']['value'] = compileObj.sub('', i['fields']['customfield_48913']['value'])

                    line = erc_file.readline()
                #print("updated key= "+i['key'])
                ###
                # target object - outjson
                outjson = {}
                content = {}
                outjson['Issue-Id'] = i['key']
                content['summary'] = i['fields']['summary']
                content['Issue Description'] = i['fields']['customfield_25119']
                content['Impact'] = i['fields']['customfield_30068']
                content['Resolution Details'] = i['fields']['customfield_39227']
                content['Test Phase(found)'] = i['fields']['customfield_19973']['value']
                content['Should have been found in (phase)'] = i['fields']['customfield_48911']['value']
                content['Should have been found in (type)'] = i['fields']['customfield_48912']['value']
                content['Reason for slippage'] = i['fields']['customfield_48913']['value']
                outjson['fields'] = content

                final_json_out.append(outjson)
                print("wrote key ="+outjson['Issue-Id'])

            final_json_key_val['Issues'] = final_json_out
            json.dump(final_json_key_val, outfile)

            print ("see file :"+inputfile_for_localAI)


