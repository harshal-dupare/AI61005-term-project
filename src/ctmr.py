import numpy as np
import copy 
import pandas as pd
from problem_model import problem
import heapq
import networkx as nx

_EPS = 1e-4

"""
Charges to maximum required if not interrupted - Travel to other node - Repeat method 
Here we charge at a node to max_capacity but if interrupted( some other EV arrives at that node ) we go to next node and allow other node to charge on that node
"""
class CTMR(object):
    def __init__(self,p):
        self.p = p
        self.events_heap = []
        self.paths = []
        self.at = []
        self.time = [] # last event time
        self.current_battery = [0 for _ in range(p.k)]
        self.node_free_charging = [-1 for _ in range(p.n)]
        self.ev_events = []
        self.evs_on_node = [[] for _ in range(p.n)]
        self.which_chrg = [-1 for _ in range(p.n)]
    
    def get_paths(self):
        for i in range(self.p.k):
            self.paths.append(nx.shortest_path(self.p.Graphs[i],source=self.p.source_node[i],target=self.p.destination_node[i], weight='weight'))
            net_b = self.p.battery_usage_on_path(i,self.paths[-1])
            if abs(net_b - self.p.initial_battery[i]) <= _EPS or  net_b < self.p.initial_battery[i]:
                self.at.append(len(self.paths[-1])-1)
                self.time.append(net_b/self.p.discharging_rate[i])
                self.ev_events.append([(self.time[-1],f"reached without charging at destination on path {self.paths[-1]}")])
                continue

            self.at.append(0)
            b = self.p.max_battery[i] - self.p.initial_battery[i]
            charge_complete_time = min(b,net_b-self.p.initial_battery[i])/self.p.charging_rate[i]
            if self.node_free_charging[self.paths[-1][0]] == -1:
                self.time.append(0)
                self.ev_events.append([(0,f"started charging at {self.paths[-1][0]}")])
                self.node_free_charging[self.paths[-1][0]] = charge_complete_time
            else:
                self.time.append(self.node_free_charging[self.paths[-1][0]])
                self.ev_events.append([(self.node_free_charging[self.paths[-1][0]],f"started charging at {self.paths[-1][0]}")])
                self.node_free_charging[self.paths[-1][0]] += charge_complete_time
        return

    def init_events(self):

        for i in range(self.p.k):
            if self.at[i]==len(self.paths[i])-1:
                continue
            net_b = self.p.battery_usage_on_path(i,self.paths[i])
            b = self.p.max_battery[i] - self.p.initial_battery[i]
            charge_complete_time = min(b,net_b-self.p.initial_battery[i])/self.p.charging_rate[i]
            self.events_heap.append((self.time[i]+charge_complete_time,i,'charging',0))
            self.evs_on_node[self.paths[i][0]].append(i)
            self.current_battery[i]=(self.p.initial_battery[i])
            self.which_chrg[self.paths[i][0]] = i 
        heapq.heapify(self.events_heap)

    def run(self):

        self.get_paths()
        self.init_events()

        while len(self.events_heap) > 0:
            event_complete_time,ev_id,etype,node_id = self.events_heap[0]
            heapq.heappop(self.events_heap)

            # if for this ev this event was overwritten by someother event earlier which changes this event
            if node_id != self.at[ev_id]:
                continue

            # if this complted event just extracted was of charging then just send it to next node to travel
            if etype == 'charging':
                # free up this node from this ev for other evs to charge
                # print(ev_id,len(self.node_free_charging),len(self.paths),len(self.paths[ev_id]),len(self.at))
                if len(self.evs_on_node[self.paths[ev_id][self.at[ev_id]]]) == 0:
                    self.node_free_charging[self.paths[ev_id][self.at[ev_id]]]=-1
                self.evs_on_node[self.paths[ev_id][self.at[ev_id]]].remove(ev_id)
                if self.which_chrg[self.paths[ev_id][self.at[ev_id]]] == ev_id:
                    self.which_chrg[self.paths[ev_id][self.at[ev_id]]] = -1
                self.ev_events[ev_id].append((event_complete_time,f"completed charging at {self.paths[ev_id][node_id]}"))
                
                u,v = self.paths[ev_id][self.at[ev_id]],self.paths[ev_id][self.at[ev_id]+1]
                edge_travel_time = self.p.time_to_travel(ev_id,(u,v))

                # print(ev_id,len(self.current_battery),len(self.time),len(self.p.charging_rate))
                self.current_battery[ev_id] = self.current_battery[ev_id]+(event_complete_time-self.time[ev_id])*self.p.charging_rate[ev_id]
                self.time[ev_id]=event_complete_time
                heapq.heappush(self.events_heap,(self.time[ev_id]+edge_travel_time,ev_id,'traveling',self.at[ev_id]+1))
                self.ev_events[ev_id].append((self.time[ev_id]+edge_travel_time,f"reached {v}"))
                self.at[ev_id]+=1

                # add the next one to charging if it exist in node u
                if len(self.evs_on_node[u]) > 0:
                    for ev_chr in self._get_charging(self.evs_on_node[u]):
                        self.which_chrg[u] = ev_chr
                        b = self.p.battery_usage_on_path(ev_chr,self.paths[ev_chr][self.at[ev_chr]:])
                        charge_complete_time = min(self.p.max_battery[ev_chr]-self.current_battery[ev_chr],b-self.current_battery[ev_chr])/self.p.charging_rate[ev_chr]
                        self.events_heap.append((event_complete_time + charge_complete_time,ev_chr,'charging',self.at[ev_chr]))
                        self.ev_events[ev_chr].append((event_complete_time,f"started charging at {u}"))
                        self.node_free_charging[u]=event_complete_time + charge_complete_time
                        self.which_chrg[u] = ev_chr
                        self.time[ev_chr] = event_complete_time

            elif etype == 'traveling':
                self.time[ev_id]=event_complete_time
                if self.at[ev_id]==len(self.paths[ev_id])-1:
                    continue

                u,v = self.paths[ev_id][self.at[ev_id]-1],self.paths[ev_id][self.at[ev_id]]

                # if ev has enough battery to finish the remaining path just let it go
                b = self.p.battery_usage_on_path(ev_id,self.paths[ev_id][self.at[ev_id]:])
                curr_b = self.current_battery[ev_id] - self.p.battery_to_travel(ev_id,(u,v))
                self.current_battery[ev_id] = curr_b
                if abs(b - curr_b) <= _EPS or  b < curr_b:
                    travel_complete_time = b/self.p.discharging_rate[ev_id]
                    self.time[ev_id]+=travel_complete_time
                    self.ev_events[ev_id].append((self.time[ev_id],f"reached destination on path {self.paths[ev_id][self.at[ev_id]:]}"))
                    self.at[ev_id]=len(self.paths[ev_id])-1
                    continue
            
                # if not enough battery calculate the charging time get complete the required charging
                charge_complete_time = (min(self.p.max_battery[ev_id]-curr_b,b-curr_b))/self.p.charging_rate[ev_id]
                if len(self.evs_on_node[v]) == 0:
                    # if no other ev is charging
                    self.events_heap.append((self.time[ev_id]+charge_complete_time,ev_id,'charging',self.at[ev_id]))
                    self.ev_events[ev_id].append((event_complete_time,f"started charging at {v}"))
                    self.time[ev_id] = event_complete_time
                    self.node_free_charging[v]=self.time[ev_id]+charge_complete_time
                    self.evs_on_node[v].append(ev_id)
                    self.which_chrg[v] = ev_id
                else:
                    # if some evs are charging
                    # take all the evs on this node and see if any of the evs can leave for the next node
                    ev_curr = self.which_chrg[v]
                    self.current_battery[ev_curr] = self.current_battery[ev_curr] + (event_complete_time-self.time[ev_curr])*self.p.charging_rate[ev_curr]
                    self.time[ev_curr] = event_complete_time
                    w = self.paths[ev_curr][self.at[ev_curr]+1]
                    req_b = self.p.battery_to_travel(ev_curr,(v,w))
                    if req_b < self.current_battery[ev_curr] or abs(req_b - self.current_battery[ev_curr])<=_EPS:
                        ## curr ev can leave
                        self.node_free_charging[v]=-1
                        self.evs_on_node[v].remove(ev_curr)
                        self.which_chrg[v] = -1
                        self.ev_events[ev_curr].append((event_complete_time,f"completed charging at {v}"))

                        self.time[ev_curr]=event_complete_time
                        edge_travel_time = self.p.time_to_travel(ev_curr,(v,w))
                        heapq.heappush(self.events_heap,(self.time[ev_curr]+edge_travel_time,ev_curr,'traveling',self.at[ev_curr]+1))
                        self.ev_events[ev_curr].append((self.time[ev_curr]+edge_travel_time,f"reached {w}"))
                        self.at[ev_curr]+=1

                    w = self.paths[ev_id][self.at[ev_id]+1]
                    req_b = self.p.battery_to_travel(ev_id,(v,w))
                    if req_b < self.current_battery[ev_id] or abs(req_b - self.current_battery[ev_id])<=_EPS:
                        ## curr ev can leave
                        # print(ev_id,v,w,event_complete_time)
                        self.time[ev_id]=event_complete_time
                        edge_travel_time = self.p.time_to_travel(ev_id,(v,w))
                        heapq.heappush(self.events_heap,(self.time[ev_id]+edge_travel_time,ev_id,'traveling',self.at[ev_id]+1))
                        self.ev_events[ev_id].append((self.time[ev_id]+edge_travel_time,f"reached {w}"))
                        self.at[ev_id]+=1
                    else:
                        self.evs_on_node[v].append(ev_id)

                    if self.which_chrg[v] == -1:
                        for ev_chr in self._get_charging(self.evs_on_node[v]):
                            self.which_chrg[v] = ev_chr
                            b = self.p.battery_usage_on_path(ev_chr,self.paths[ev_chr][self.at[ev_chr]:])
                            charge_complete_time = min(self.p.max_battery[ev_chr]-self.current_battery[ev_chr],b-self.current_battery[ev_chr])/self.p.charging_rate[ev_chr]
                            self.events_heap.append((event_complete_time + charge_complete_time,ev_chr,'charging',self.at[ev_chr]))
                            self.ev_events[ev_chr].append((event_complete_time,f"started charging at {v}"))
                            self.node_free_charging[v]=event_complete_time + charge_complete_time
                            self.which_chrg[v] = ev_chr
                            self.time[ev_chr] = event_complete_time
                            
            heapq.heapify(self.events_heap)
        
    def _get_charging1(self,ev_list):
        if len(ev_list) > 0:
            return [ev_list[0]]
        return []

    def _get_charging(self,ev_list):
        if len(ev_list) > 0:
            b_ev = ev_list[0]
            b_vl =  self.p.battery_usage_on_path(b_ev,self.paths[b_ev][self.at[b_ev]:])
            for ev in ev_list:
                tvl = self.p.battery_usage_on_path(ev,self.paths[ev][self.at[ev]:])
                if tvl > b_vl:
                    b_ev = ev
                    b_vl = tvl
            return [b_ev]         
        return []


    def print_paths(self):
        for i in range(self.p.k):
            print(f"for EV {i} : {self.ev_events[i]}")
        return

p = problem.problem()

p.input("gen_testcase.txt")

p.make_graphs()

Thr_min = p.theoritical_minima()
print("Lower bound is: ",Thr_min,"\n")

sol = CTMR(p)
sol.run()

# print(sol.time)
print("output of algoritm is: ",np.max(sol.time),"\n")

print("Paths that are followed are:\n")
sol.print_paths()