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
    print("INPUTS: SHM-only-usage-analysis#1 SHM-only-usage-analysis#2 Analysis_title")
    exit()

print("INPUT: analysis#1: ",sys.argv[1])
print("INPUT: analysis#2: ",sys.argv[2])
print("INPUT: analysis#Title: ",sys.argv[3])


## Operator config file:
## ma-operator mapping file
## 
# internal file for stats
opr_mapping_file_path = "c:/Users/xgurpat/OneDrive - Ericsson/SHMonly/MA-operator-mapping.json"


#SHMOpr_file = "SHM-Opr_Wk1-Wk33.txt"
#ASU_file= "ASU_STATS_2024_WK1-WK33.csv"
#ASU_file= "ASU_STATS_2022_WK1-WK52.csv"
analysis_1_file = sys.argv[1]

#SHM_raw_stats_file = "SHM_STATS_UPGRADE2024_WK1-WK33.csv"
#SHM_raw_stats_file = "SHM_STATS_2022_WK1-WK52.csv"
analysis_2_file = sys.argv[2]

analysis_title = sys.argv[3]


now = datetime.now()
datetime_str = now.strftime("%d-%m-%Y_%H-%M-%S")

#Output
#print out
outcontent={}
outFilePath="compare_SHM-Opr-not-using-ASU.json"
Out_pdffile = "compare_SHM-only-Usage"

  
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

# read-config obj
analysis_1_stats = {}
analysis_2_stats = {}


with open(analysis_1_file, 'r', encoding="utf-8") as json_1_file:
    analysis_1_stats = json.load(json_1_file)
print("READ: ", analysis_1_file)

with open(analysis_2_file, 'r', encoding="utf-8") as json_2_file:
    analysis_2_stats = json.load(json_2_file)
print("READ: ", analysis_2_file)

unique_1_list = []
common_1_list = []

for i in analysis_1_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].keys():
    if  analysis_2_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].get(i):
        common_1_list.append(i)
    else:
        unique_1_list.append(i)

"""
print("Total length of 1: ",len(analysis_1_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].keys()))
print("Total length of 2: ",len(analysis_2_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].keys()))

print("No. of unique in 1 ", len(unique_1_list)," values: ",unique_1_list)    
print("No. of common in 1 ", len(common_1_list)," values: ",common_1_list)    
"""

##
#write output
##

# dump this info
outcontent['inputs'] = {}
outcontent['inputs']['file_1'] = analysis_1_file
outcontent['inputs']['file_2'] = analysis_2_file
outcontent['inputs']['time_of_processing'] = datetime_str

outcontent['comparison'] = {}

outcontent['comparison']['stats'] = {}
outcontent['comparison']['stats']['Total_file_1-Opr'] = len(analysis_1_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].keys())
outcontent['comparison']['stats']['Total_file_2-Opr'] = len(analysis_2_stats["SHM_only_Usage_analysis"]["top_operators_across_MA"].keys())
outcontent['comparison']['stats']['No of common-Opr'] = len(common_1_list)
outcontent['comparison']['stats']['No of unique-Opr_file_1'] = len(unique_1_list)

outcontent['comparison']['unique_operators_in_file_1'] = unique_1_list
outcontent['comparison']['common_operators_in_file_1'] = common_1_list


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









