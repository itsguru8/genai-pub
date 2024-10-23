import sys
import os
import re
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages 

import numpy as np
from datetime import datetime
import pandas

## Input:
## 1.  ASU usage file txt
## 2. SHM usage file 
if (len(sys.argv) < 4) :
    print("INPUTS: <asu_raw_stats_file> <shm_raw_stats_file> <description> ")
    exit()

print("INPUT: asu_raw_stats_file: ",sys.argv[1])
print("INPUT: shm_raw_stats_file: ",sys.argv[2])


## Operator config file:
## ma-operator mapping file
## 
# internal file for stats
opr_mapping_file_path = "c:/Users/xgurpat/OneDrive - Ericsson/SHMonly/MA-operator-mapping.json"


#ASU_file= "ASU_STATS_2022_WK1-WK52.csv"
ASU_file = sys.argv[1]

#SHM_raw_stats_file = "SHM_STATS_2022_WK1-WK52.csv"
SHM_raw_stats_file = sys.argv[2]


#vars
asu_opr_list = {}
shm_only_all_stats = {}

shm_opr_using_asu = {} 
shm_opr_using_asu_count = 0
total_shm_opr_using_asu_count = 0
shm_opr_NOT_using_asu = {} 
shm_opr_NOT_using_asu['shm_opr_NOT_using_asu_count'] = 0

#across MA, top operators
shm_opr_NOT_using_asu_nodes_count = {}

now = datetime.now()
datetime_str = now.strftime("%d-%m-%Y_%H-%M-%S")

#Output
#print out
outcontent={}
outFilePath = sys.argv[3] + ".json"
Out_pdffile = sys.argv[3]+"_"+datetime_str+".pdf"

# [2] method to know if a given SHM opr using ASU ?
def if_opr_using_ASU(l_opr):
    if asu_opr_list.get(l_opr):
        return True
    else:
        return False
        
# test [2]
def test_func(l_test_opr):
    if if_opr_using_ASU(l_test_opr) :
        print(l_test_opr," is using ASU")
    else:
        print(l_test_opr, " is NOT using ASU")

#test_opr = "BELL-CA"
#test_func(test_opr)


def dump_ma_stats(l_ma,x_label,y_label) :
    empty_keys = [k for k,v in shm_only_all_stats[l_ma].items() if v == 0]
    for k in empty_keys:
        del shm_only_all_stats[l_ma][k]
    sorted_ma_stats = dict(sorted(shm_only_all_stats[l_ma].items(), key=lambda item:item[1], reverse=True)) 
    #print (sorted_ma_stats)   
    shm_only_all_stats[l_ma] = sorted_ma_stats
    
    if len(sorted_ma_stats):
        shm_only_all_stats[l_ma]["Operator_Count"] = len(sorted_ma_stats) - 1

        plot_names = np.array(list(sorted_ma_stats.keys()))
        print(plot_names)
        plot_names = np.char.replace(plot_names,"-","\n")
        plot_values = np.array(list(sorted_ma_stats.values()))
        plt.bar(plot_names[0:6], plot_values[0:6])
        for i in range(len(plot_names[0:6])):
            plt.text(i, plot_values[i], plot_values[i], ha = 'center', fontsize = 8)

        #plt.show()
        plt.title(l_ma)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(fontsize = 8)
        plt.figure()
    
def save_image(pdffile): 
    p = PdfPages(pdffile)       
    fig_nums = plt.get_fignums()   
    figs = [plt.figure(n) for n in fig_nums] 
      
    for fig in figs:  
        fig.savefig(p, format='pdf')  
    p.close()   

## MAIN ##


## check before running

#[XXXX]1. input file names should have only one '.' , no more dots expected
# 2. the xlsx sheet name & input file name should match
#3. the xlsx files should be closed when running the script
#[XXXX]4. if script still fails due to unknown operator, update the MA config mapping file under appropriate MA
#5. the input files should not have "," within the file content. else parse fails. e.g: "Preparation, Activation" under "Phases" column


# read-config obj 
with open(opr_mapping_file_path, 'r', encoding="utf-8") as json_file:
    shm_only_all_stats = json.load(json_file)
print("READ: config file: ", opr_mapping_file_path)

# [1] get ASU opr list
#Site,Deployment Type,Market Area,ENM Version,Operator,Flow Execution Name,Phases,Start Time,End Time,Duration,Node Count

#
#read from excel
if "xlsx" in ASU_file:
    file1_out = os.path.basename(ASU_file)
    file1_out = ''.join(file1_out.split('.')[0]) # sheetname: get file name without extesion
    excel_data_df = pandas.read_excel(ASU_file, sheet_name=file1_out)
    file1_out += "_.csv"
    excel_data_df.to_csv(file1_out, index=False,mode='w+')
    #post-sheet extraction, use it as input ASU file  
    ASU_file = file1_out
else :
    if not "csv" in ASU_file:
        print("ERR: input ASU file is not valid raw stats file of ext: xlsm/csv  ")
        exit()

print("ASU raw stats file: ",ASU_file)
#end -read from excel

#test
#exit()

# now parse ASU csv
with open(ASU_file) as asu_File:
    asu_lines = asu_File.readlines()
    #remove header
    asu_lines.pop(0)
    for line in asu_lines:
        asu_opr = ''.join(line.split(',')[4])
        if asu_opr :   # null check
          if not asu_opr_list.get(asu_opr):
              #print("adding opr to list: ",asu_opr)
              asu_opr_list[asu_opr] = 0
          asu_node_count = int(''.join(line.split(',')[10]))
          asu_opr_list[asu_opr] += asu_node_count

# [2] method tocheck asu usage if_opr_using_ASU
print("READ: No.  of ASU opr:",len(asu_opr_list))


# [3] Main algo - parse each SHM raw stat
#Site,Deployment Type,Market Area,ENM Version,Operator,JobType,NodeCount,JobName,StartTime,EndTime,Duration,Status,Progress,Result,WKNO

if "xlsx" in SHM_raw_stats_file:
    file2_out = os.path.basename(SHM_raw_stats_file)
    file2_out = ''.join(file2_out.split('.')[0]) # get file name without extesion
    excel_data_df2 = pandas.read_excel(SHM_raw_stats_file, sheet_name=file2_out)
    file2_out += "_.csv"
    excel_data_df2.to_csv(file2_out, index=False,mode='w+')
    #overwrite input SHM file name
    SHM_raw_stats_file = file2_out
    print("SHM raw stats file: ",SHM_raw_stats_file)
else :
    if not "csv" in SHM_raw_stats_file:
        print("ERR: input SHM file is not valid raw stats file of ext: xlsm/csv  ")
        exit()

print("SHM raw stats file: ",SHM_raw_stats_file)

# now parse SHM csv
with open(SHM_raw_stats_file, "r") as SHM_raw_stats:
    lines = SHM_raw_stats.readlines()
    #remove header
    lines.pop(0)

    for line in lines:
        shm_job_type = ''.join(line.split(',')[5])

        if "UPGRADE" not in shm_job_type :
            continue

        shm_opr = ''.join(line.split(',')[4]) # "opr" name e.g. STC-SA, Zain-BH
        l_ma = ''.join(line.split(',')[2]) # market area
        l_cnt = int(''.join(line.split(',')[6])) # node count

        if if_opr_using_ASU(shm_opr) :
            """
            if not shm_opr_using_asu.get(shm_opr):
                shm_opr_using_asu[shm_opr] = 1 # first time, create key
                shm_opr_using_asu_count += 1
                #shm_opr_using_asu[shm_opr] += l_cnt
                #total_shm_opr_using_asu_count += l_cnt
                print(shm_opr," is using ASU!")
            """
            continue  # good, seems SHM opr also using ASU ! nothing to do
        else:  # get stats            
            if not shm_opr_NOT_using_asu.get(shm_opr):
                shm_opr_NOT_using_asu[shm_opr] = 1  #set some value , so that prev line is false next time & we avoid double count of #opr
                shm_opr_NOT_using_asu['shm_opr_NOT_using_asu_count'] += 1
                #print("Not using ASU: ma: ",l_ma,", opr:",shm_opr)
                shm_opr_NOT_using_asu_nodes_count[shm_opr] = 0 #create key for node count

            # stat by Operator
            shm_opr_NOT_using_asu_nodes_count[shm_opr] += l_cnt
            shm_only_all_stats['all_nodes_count'] += l_cnt

            # stat by MA
            if shm_only_all_stats.get(l_ma):
                shm_only_all_stats[l_ma]['nodes_count'] += l_cnt

                if not shm_only_all_stats[l_ma].get(shm_opr):
                    shm_only_all_stats[l_ma][shm_opr] = 0

                shm_only_all_stats[l_ma][shm_opr] += l_cnt
            else:
                print("ma: ",l_ma,", MA not found!")
                exit()


# [4] get-stats
shm_only_all_stats["total_operator_Count"] = shm_opr_NOT_using_asu['shm_opr_NOT_using_asu_count']

##
#write output
##


##
#PLOTS
#plot top 10 operators
sorted_overall_stats = dict(sorted(shm_opr_NOT_using_asu_nodes_count.items(), key=lambda item:item[1], reverse=True))    
shm_only_all_stats["top_operators_across_MA"] = sorted_overall_stats
top_plot_names = np.array(list(sorted_overall_stats.keys()))
#print(top_plot_names)
top_plot_names = np.char.replace(top_plot_names,"-","\n")

top_plot_values = np.array(list(sorted_overall_stats.values()))
plt.bar(top_plot_names[0:20], top_plot_values[0:20])
for i in range(len(top_plot_names[0:20])):
    plt.text(i, top_plot_values[i], top_plot_values[i], ha = 'center', fontsize = 6)

plt.title("Top SHM Upgrade Operators - not using ASU")
plt.xlabel("Operator")
plt.ylabel("Nodes in Upgrade")
plt.xticks(rotation = 50, fontsize = 6)
plt.figure()

for i_ma in shm_only_all_stats["nodes_by_MA"]:
    print("processing..",i_ma)
    shm_only_all_stats["nodes_by_MA"][i_ma] = shm_only_all_stats[i_ma]['nodes_count']
    dump_ma_stats(i_ma,"Operator","Nodes in Upgrade")

#plot overall ma stats
sorted_overall_ma_stats = dict(sorted(shm_only_all_stats["nodes_by_MA"].items(), key=lambda item:item[1], reverse=True))    
shm_only_all_stats["nodes_by_MA"] = sorted_overall_ma_stats
o_plot_names = np.array(list(sorted_overall_ma_stats.keys()))
o_plot_values = np.array(list(sorted_overall_ma_stats.values()))
plt.bar(o_plot_names, o_plot_values)
for i in range(len(o_plot_names)):
    plt.text(i, o_plot_values[i], o_plot_values[i], ha = 'center', fontsize = 6)

plt.title("All MA stats")
plt.xlabel("MA")
plt.ylabel("Nodes in Upgrade")
plt.figure()


save_image(Out_pdffile)
print("[READY]see plots file(s): ",Out_pdffile)

# dump this info
outcontent['inputs'] = {}
outcontent['inputs']['asu_raw_stats_file'] = ASU_file
outcontent['inputs']['shm_raw_stats_file'] = SHM_raw_stats_file
outcontent['inputs']['time_of_processing'] = datetime_str
outcontent['asu'] = {}
outcontent['asu']['no. of ASU operators'] = len(asu_opr_list)
outcontent['asu']['asu_operators'] = asu_opr_list

outcontent['SHM_only_Usage_analysis'] = shm_only_all_stats


#outcontent['SHM_opr_Using_ASU'] = {}
#outcontent['SHM_opr_Using_ASU']['shm_opr_using_asu_count'] =  shm_opr_using_asu_count

with open(outFilePath, "w+") as outfile:
    json.dump(outcontent, outfile)
    print("[READY]see results file(s): ",outFilePath)







