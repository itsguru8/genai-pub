import sys
import os
import re
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages 

import numpy as np
from datetime import datetime

## Input:
## 1. SHM-only-usage-analysis#1
## 2. SHM-only-usage-analysis#2
if (len(sys.argv) < 4) :
    print("INPUTS: ZTI-usage-analysis#1 SHM-only-usage-analysis#2 Analysis_title")
    exit()

print("INPUT: analysis#1: ",sys.argv[1])
print("INPUT: analysis#2: ",sys.argv[2])
print("INPUT: analysis#Title: ",sys.argv[3])


## Operator config file:
## ma-operator mapping file
## 
# internal file for stats
opr_mapping_file_path = "c:/Users/xgurpat/OneDrive - Ericsson/SHMonly/MA-operator-mapping.json"


#AP_ZT_Usage_08_Oct_rawStats
analysis_1_file = sys.argv[1]

#AP_ZT_Usage_31_Dec_2023_rawStats
analysis_2_file = sys.argv[2]

analysis_title = sys.argv[3]

now = datetime.now()
datetime_str = now.strftime("%d-%m-%Y_%H-%M-%S")

#Output
#print out
outcontent={}
outFilePath="compare_ZTI-Opr-not-using-ASU.json"
Out_pdffile = "compare_ZTI-Usage"

  
def save_image(pdffile): 
    p = PdfPages(pdffile)       
    fig_nums = plt.get_fignums()   
    figs = [plt.figure(n) for n in fig_nums] 
      
    for fig in figs:  
        fig.savefig(p, format='pdf')  
    p.close()   




####################################################################################################################
## MAIN ##
####################################################################################################################

analysis_1_stats = {}
analysis_2_stats = {}

#Row Labels,Count of nodeName
#Airtel_Libreville_ltcenm01lms,11
f1_ZTI_opr_node_count = {}
with open(analysis_1_file, "r") as raw_1_stats:
    lines = raw_1_stats.readlines()
    #remove header
    lines.pop(0)

    for line in lines:
        site = ''.join(line.split(',')[0]) # Airtel_Libreville_ltcenm01lms,
        nodes = int(''.join(line.split(',')[1])) # Airtel_Libreville_ltcenm01lms,
        l_opr = ''.join(line.split('_')[0]) # Airtel

        if not f1_ZTI_opr_node_count.get(l_opr):
            f1_ZTI_opr_node_count[l_opr] = 0 # create key 1st time
            #print("Not using ASU: ma: ",l_ma,", opr:",shm_opr)
        f1_ZTI_opr_node_count[l_opr] += nodes


#Row Labels,Count of nodeName
#Airtel_Libreville_ltcenm01lms,11
f2_ZTI_opr_node_count = {}
with open(analysis_2_file, "r") as raw_2_stats:
    lines = raw_2_stats.readlines()
    #remove header
    lines.pop(0)

    for line in lines:
        site = ''.join(line.split(',')[0]) # Airtel_Libreville_ltcenm01lms,
        nodes = int(''.join(line.split(',')[1])) # Airtel_Libreville_ltcenm01lms,
        l_opr = ''.join(line.split('_')[0]) # Airtel

        if not f2_ZTI_opr_node_count.get(l_opr):
            f2_ZTI_opr_node_count[l_opr] = 0 # create key 1st time
            #print("Not using ASU: ma: ",l_ma,", opr:",shm_opr)
        f2_ZTI_opr_node_count[l_opr] += nodes

# now compare f1 & f2 results
"""
{
    "inputs": {
        "file_1": ".\\SHM-Opr-not-using-ASU.json",
        "file_2": ".\\2023\\SHM-Opr-not-using-ASU.json",
        "time_of_processing": "07-10-2024_22-21-15"
    },
    "comparison": {
        "stats": {
            "Total_file_1-Opr": 159,
            "Total_file_2-Opr": 141,
            "No of common-Opr": 99,
            "No of unique-Opr_file_1": 60
        },
        "unique_operators_in_file_1": {
            "PT-ID" : x,
            ...
		},
		"common_operators_in_file_1": {
            "KoreaTelecom-KR" : y,
            ...
        },
        "unique_operators_in_file_2": {
            "ABC_opr" : z,
            ...
	    }
	 }
}
"""

unique_1_list = {}
common_1_list = {}
unique_2_list = {}

for i in f1_ZTI_opr_node_count.keys():
    if  f2_ZTI_opr_node_count.get(i):
        common_1_list[i] = f1_ZTI_opr_node_count[i]
    else:
        unique_1_list[i] = f1_ZTI_opr_node_count[i]

for j in f2_ZTI_opr_node_count.keys():
    if  not common_1_list.get(j):
        unique_2_list[j] = f2_ZTI_opr_node_count[j]


#dump this info
outcontent['inputs'] = {}
outcontent['inputs']['file_1'] = analysis_1_file
outcontent['inputs']['file_2'] = analysis_2_file
outcontent['inputs']['time_of_processing'] = datetime_str

outcontent['comparison'] = {}

outcontent['comparison']['stats'] = {}
outcontent['comparison']['stats']['Total_file_1-Opr'] = len(f1_ZTI_opr_node_count.keys())
outcontent['comparison']['stats']['Total_file_2-Opr'] = len(f2_ZTI_opr_node_count.keys())
outcontent['comparison']['stats']['No of common-Opr'] = len(common_1_list)
outcontent['comparison']['stats']['No of unique-Opr_file_1'] = len(unique_1_list)

outcontent['comparison']['unique_operators_in_file_1'] = unique_1_list
outcontent['comparison']['common_operators_in_file_1'] = common_1_list
outcontent['comparison']['unique_operators_in_file_2'] = unique_2_list


##
#write output
##

with open(outFilePath, "w+") as outfile:
    json.dump(outcontent, outfile)
    print("[READY]see Compare results file(s): ",outFilePath)


##
#PLOTS
o_plot_names = np.array(list(outcontent['comparison']['stats'].keys()))
o_plot_names = np.char.replace(o_plot_names,"-","\n")
     
o_plot_values = np.array(list(outcontent['comparison']['stats'].values()))
plt.bar(o_plot_names, o_plot_values)
for i in range(len(o_plot_names)):
    plt.text(i, o_plot_values[i], o_plot_values[i], ha = 'center', fontsize = 6)

#plt.title("Node Upgrade: SHM_Only_Operator 2024_Wk1-Wk33 vs 2023")
plt.title(analysis_title)
plt.xlabel("stats")
plt.ylabel("values")
plt.figure()

#finally write everything to pdf file
Out_pdffile += datetime_str+".pdf"

save_image(Out_pdffile)
print("[READY]see plots file(s): ",Out_pdffile)









