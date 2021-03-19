import numpy as np
import copy 
import pandas as pd
from problem_model import problem
import heapq
import networkx as nx

_EPS = 1e-4

"""
Charge to maximum required - Travel to other node - Repeat method 
"""
class CTR(object):
    def __init__(self,p):
        self.p = p
        self.events_heap = []
        self.paths = []
        self.at = []
        self.time = []
        self.node_free_charging = [-1 for _ in range(p.n)]
        self.ev_events = []
    
    def get_paths(self):
        for i in range(self.p.k):
            self.paths.append(nx.shortest_path(self.p.Graphs[i],source=self.p.source_node[i],target=self.p.destination_node[i], weight='weight'))
            self.at.append(0)
            self.time.append(0)
            self.ev_events.append([(0,f"started charging at {self.paths[-1][0]}")])
            b = self.p.battery_usage_on_path(i,self.paths[-1])
            if abs(b - self.p.initial_battery[i]) <= _EPS or  b < self.p.initial_battery[i]:
                self.at[-1]=len(self.paths[-1])-1
                self.time[-1] = b/self.p.discharging_rate[i]
                self.ev_events[-1] = [(self.time[-1],f"reached without charging at destination on path {self.paths[-1]}")]
                continue
        return

    def init_events(self):
        for i in range(self.p.k):
            if self.at[i]==len(self.paths[i])-1:
                continue
            net_b = self.p.battery_usage_on_path(i,self.paths[i])
            b = self.p.max_battery[i] - self.p.initial_battery[i]
            charge_complete_time = min(b,net_b-self.p.initial_battery[i])/self.p.charging_rate[i]
            self.events_heap.append((self.time[i]+charge_complete_time,i,'charging'))
            self.node_free_charging[self.paths[i][0]]=self.time[i]+charge_complete_time
            self.ev_events[i].append((self.time[i]+charge_complete_time,f"completed charging at {self.paths[i][0]}"))
        heapq.heapify(self.events_heap)

    def run(self):

        self.get_paths()
        self.init_events()

        while len(self.events_heap) > 0:
            event_complete_time,ev_id,etype = self.events_heap[0]
            heapq.heappop(self.events_heap)

            if etype == 'charging':
                if abs(self.node_free_charging[self.paths[ev_id][self.at[ev_id]]]-event_complete_time)<=_EPS:
                    self.node_free_charging[self.paths[ev_id][self.at[ev_id]]]=-1
                self.time[ev_id]=event_complete_time
                u,v = self.paths[ev_id][self.at[ev_id]],self.paths[ev_id][self.at[ev_id]+1]
                edge_travel_time = self.p.time_to_travel(ev_id,(u,v))
                heapq.heappush(self.events_heap,(self.time[ev_id]+edge_travel_time,ev_id,'traveling'))
                self.ev_events[ev_id].append((self.time[ev_id]+edge_travel_time,f"reached {v}"))
            elif etype == 'traveling':
                self.at[ev_id]+=1
                self.time[ev_id]=event_complete_time
                if self.at[ev_id]==len(self.paths[ev_id])-1:
                    continue

                u,v = self.paths[ev_id][self.at[ev_id]-1],self.paths[ev_id][self.at[ev_id]]

                b = self.p.battery_usage_on_path(ev_id,self.paths[ev_id][self.at[ev_id]:])
                curr_b = self.p.max_battery[ev_id] - self.p.battery_to_travel(ev_id,(u,v))
                if abs(b - curr_b) <= _EPS or  b < curr_b:
                    travel_complete_time = b/self.p.discharging_rate[ev_id]
                    self.time[ev_id]+=travel_complete_time
                    self.ev_events[ev_id].append((self.time[ev_id],f"reached destination on path {self.paths[ev_id][self.at[ev_id]:]}"))
                    self.at[ev_id]=len(self.paths[ev_id])-1
                    continue
                
                charge_complete_time = (min(self.p.max_battery[ev_id]-curr_b,b-curr_b))/self.p.charging_rate[ev_id]
                if self.node_free_charging[v] == -1:
                    # print(ev_id,v,len(self.paths),len(self.paths[ev_id]),len(self.time))
                    self.events_heap.append((self.time[ev_id]+charge_complete_time,ev_id,'charging'))
                    self.ev_events[ev_id].append((self.time[ev_id]+charge_complete_time,f"completed charging at {v}"))
                    self.node_free_charging[v]=self.time[ev_id]+charge_complete_time
                else:
                    self.events_heap.append((max(self.time[ev_id],self.node_free_charging[v])+charge_complete_time,ev_id,'charging'))
                    self.ev_events[ev_id].append((max(self.time[ev_id],self.node_free_charging[v])+charge_complete_time,f"completed charging at {v}"))
                    self.node_free_charging[v]=max(self.time[ev_id],self.node_free_charging[v])+charge_complete_time
            
            heapq.heapify(self.events_heap)
        
    def print_paths(self):
        for i in range(self.p.k):
            print(f"for EV {i} : {self.ev_events[i]}")
        return

p = problem.problem()

p.input("gen_testcase.txt")

p.make_graphs()

# print(p)

print(p.theoritical_minima())

sol = CTR(p)

sol.run()

print(sol.time)

print(np.max(sol.time))
sol.print_paths()