#!/usr/bin/python

import json, sys, os
from datetime import datetime, timedelta

def get_dic_list(json_list):
    dic_list = []
    for line in json_list:
        dic = json.loads(line)
        if (len(dic) == 3) and ('' not in dic.values()):
            dic_list.append(dic)
    return dic_list

def trunc(num, digit):
    # using "format" (it rounds the number) works here since the decimals we would get are 
    # either .00 or .50 which wouldn't be modified numerically.
    return format(num,'.2f')

def median(deg_list):
    deg_list = sorted(deg_list)
    n = len(deg_list)
    if n < 1:
        return None
    if n %2 == 1:
        return trunc(deg_list[n/2], 2)
    else:
        return trunc((deg_list[(n/2)-1] + deg_list[n/2])/2.0, 2)

def get_deg_list(graph):
    deg_list = []
    for user in graph:
        deg_list.append(len(graph[user]))
    return deg_list

def get_relevant_index_list(dic_list):
    n = len(dic_list)
    relevant_index = [0]
    relevant_index_list = []
    relevant_index_list.append(relevant_index[:])
    
    time_list = []
    for i in range(0,n):
        time_list.append(datetime.strptime(dic_list[i]['created_time'], "%Y-%m-%dT%H:%M:%SZ"))
   
    max_time = time_list[0]
    
    for i in range(1,n):
        if time_list[i] >= max_time:
            max_time = time_list[i]
            for j in relevant_index[:]:
                if (max_time - time_list[j]) >= timedelta(seconds=60):
                    relevant_index.remove(j)
            relevant_index.append(i)
        elif (max_time - time_list[i]) < timedelta(seconds=60):
            relevant_index.append(i)
        relevant_index_list.append(relevant_index[:])
        
    return relevant_index_list

def get_rolling_median(dic_list):
    rolling_median = []
    n = len(dic_list)
    if n < 1: return None
    
    relevant_index_list = get_relevant_index_list(dic_list)
    
    for indexes in relevant_index_list:
        graph = {}
        for index in indexes:
            actor = dic_list[index]['actor']
            target = dic_list[index]['target']
            if (actor not in graph) and (target not in graph):
                graph[actor] = [target]
                graph[target] = [actor]
            if (actor not in graph) and (target in graph):
                graph[actor] = [target]
                graph[target].append(actor)
            if (actor in graph) and (target not in graph):
                graph[actor].append(target)
                graph[target] = [actor]
            if (actor in graph) and (target not in graph[actor]):
                graph[actor].append(target)
                graph[target].append(actor)
        deg_list = get_deg_list(graph)
        rolling_median.append(median(deg_list))
    
    return rolling_median

def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print "usage: [input file] [output file]";
        sys.exit(1)
    input_file = args[0]
    output_file = args[1]

    with open( input_file, 'r' ) as in_f:
        json_list = in_f.read().split('\n')
        del json_list[-1]
        
    dic_list = get_dic_list(json_list)
    rolling_median =  get_rolling_median(dic_list)
    rolling_median_txt = '\n'.join(rolling_median) + '\n'

    if not os.path.exists('./venmo_output'): os.mkdir('./venmo_output')
    with open( output_file, 'w+') as out_f:
        out_f.write(rolling_median_txt)

if __name__ == "__main__":
    main()

