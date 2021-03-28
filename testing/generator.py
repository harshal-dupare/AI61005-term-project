import networkx as nx
import random
import numpy as np
from tqdm import tqdm

# generate weigted random connected graph with diff m/n ratios
# decide number of EVs
# pick source and destination for each EV, no more than 2 EVs on same source
# asssign speed, discharge_rate, charging rate
# find max weight edge on a random path from s->d assign for some k>0 discharge_rate*(1+k)*max_weight_dist/speed as max_battery_capacity
# assign initial battery

filename = "gen_testcase.txt"

_output_file = open(filename,'w')

min_n, max_n = 3,30
min_w,max_w = 1,100
n = random.randint(min_n,max_n)
min_k,max_k = 1,int(n*0.5)
min_cr,max_cr = 1,max_w*0.1
min_dcr,max_dcr = 1,max_w*0.1
min_sp,max_sp = 1,max_w*0.1

while True:
    # G = nx.erdos_renyi_graph(n, 0.5, seed=random.randint(0,1000), directed=False)
    # G = nx.karate_club_graph()
    G = nx.generators.trees.random_tree(n,seed=random.randint(0,1000))
    if nx.is_connected(G):
        break

n = G.number_of_nodes()
m = G.number_of_edges()
_output_file.write(str(n)+'\n')
_output_file.write(str(m)+'\n')

for edg in G.edges(data=True):
    W = min_w+(max_w-min_w)*random.random()
    G[edg[0]][edg[1]]['weight'] = W
    _output_file.write(str(edg[0])+' '+str(edg[1])+' '+str(W)+'\n')    

print("Graph Completed")

k = random.randint(min_k,max_k)
_output_file.write(str(k)+'\n')    

_output_file.flush()

source_node = list(np.random.choice(list(range(n))+list(range(n)),k,replace=False))
temp = list(np.random.choice(list(range(n))+list(range(n)),2*n))
destination_node = []
id = 0
i = 0
while i < k:
    if temp[id] == source_node[i]:
        id+=1
        id = id%(2*n)
        continue
    destination_node.append(temp[id])
    i+=1
    id+=1

charging_rate = [ min_cr+(max_cr-min_cr)*random.random() for _ in range(k)]
discharging_rate =[ min_dcr+(max_dcr-min_dcr)*random.random() for _ in range(k)]
speed = [ min_sp+(max_sp-min_sp)*random.random() for _ in range(k)]

print("Source destination and params completed")

def get_max_weight(path):
    max_w = -1
    for i in range(1,len(path)):
        max_w = max(G[path[i-1]][path[i]]['weight'],max_w)
    return max_w

iter_count_max_weight = 4
max_edge_weight = []
# for i in range(k):
#     gpath = list(nx.all_simple_paths(G, source=source_node[i], target=destination_node[i]))
#     ridx = np.random.choice(list(range(len(gpath))),size=min(iter_count_max_weight,len(gpath)),replace=False)
#     max_w = -1
#     for j in ridx:
#         max_w = max(max_w,get_max_weight(gpath[j]))
#     max_edge_weight.append(max_w)


for i in tqdm(range(k)):
    titer_count_max_weight = iter_count_max_weight
    gpath = (nx.all_simple_paths(G, source=source_node[i], target=destination_node[i]))
    lpath = []
    for pt in gpath:
        lpath.append(pt)
        titer_count_max_weight-=1
        if titer_count_max_weight==0:
            break
    max_w = -1
    for ipath in lpath:
        max_w = max(max_w,get_max_weight(ipath))
    max_edge_weight.append(max_w)

print("Max weight Completed")

capacity_to_max_edge_multiplier = 2
max_battery = [ max_edge_weight[i]*(1+random.random()*capacity_to_max_edge_multiplier)*discharging_rate[i]/speed[i] for i in range(k)]
initial_battery=[max_battery[i]*random.random() for i in range(k)]

for i in range(k):
    _output_file.write(str(source_node[i])+' ')
    _output_file.write(str(destination_node[i])+' ')
    _output_file.write(str(initial_battery[i])+' ')
    _output_file.write(str(charging_rate[i])+' ')
    _output_file.write(str(discharging_rate[i])+' ')
    _output_file.write(str(max_battery[i])+' ')
    _output_file.write(str(speed[i])+'\n')

_output_file.close()