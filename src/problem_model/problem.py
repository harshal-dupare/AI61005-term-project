import numpy as np
import copy
import pandas as pd
import networkx as nx


class problem(object):
    def __init__(self):
        self.n = 0
        self.m = 0
        self.k = 0
        self.source_node = []
        self.destination_node = []
        self.initial_battery = []
        self.charging_rate = []
        self.discharging_rate = []
        self.max_battery = []
        self.speed = []
        self.edge_list = dict()

        self._df = pd.DataFrame()
        self.graph_made = False
        self.Graphs = []
        self.current_node = []

        pass

    def __str__(self):
        """
        Needs complete to string funtion
        """
        _s = "================================\n"
        _s += f"Number of cities: {self.n}\n"
        _s += f"Number of roads: {self.m}\n"
        _s += f"Number of roads: {self.m}\n================================\n"
        _s += f"Roads:\n{self.edge_list}\n================================\n"
        _s += f"{self._df}"
        return _s

    def time_to_travel(self, i, edg):
        return (self.edge_list[edg]/self.speed[i])

    def battery_to_travel(self, i, edg):
        return (self.edge_list[edg]/self.speed[i])*self.discharging_rate[i]

    def battery_usage_on_path(self,i, path):
        total_battery_usage = 0
        for j in range(1,len(path)):
            total_battery_usage+=(self.edge_list[(path[j-1],path[j])]/self.speed[i])*self.discharging_rate[i]
        return total_battery_usage

    def input(self,filename=None):
        
        if type(filename)==type(None):
            self.n = int(input("Number of cities"))
            self.m = int(input("Number of roads"))
            print(f"For next {self.m} lines give input of u,v are city index 0-based w is distance : u v w")
            for _ in range(self.m):
                _l = input().split(' ')
                self.edge_list[(int(_l[0]),int(_l[1]))]=float(_l[2])
                self.edge_list[(int(_l[1]),int(_l[0]))]=float(_l[2])

            self.k = int(input("Number of Ev's"))
            print("For each EV input 7 space seperated numbers: Sr Dr Br cr dr Mr sr")
            for _ in range(self.k):
                _l = input().split(' ')
                self.source_node.append(int(_l[0]))
                self.destination_node.append(int(_l[1]))
                self.initial_battery.append(float(_l[2]))
                self.charging_rate.append(float(_l[3]))
                self.discharging_rate.append(float(_l[4]))
                self.max_battery.append(float(_l[5]))
                self.speed.append(float(_l[6]))
        else:
            _input_file = open(filename,'r')

            self.n = int(_input_file.readline())
            self.m = int(_input_file.readline())
            for _ in range(self.m):
                _l = _input_file.readline().split(' ')
                self.edge_list[(int(_l[0]),int(_l[1]))]=float(_l[2])
                self.edge_list[(int(_l[1]),int(_l[0]))]=float(_l[2])

            self.k = int(_input_file.readline())
            for _ in range(self.k):
                _l = _input_file.readline().split(' ')
                self.source_node.append(int(_l[0]))
                self.destination_node.append(int(_l[1]))
                self.initial_battery.append(float(_l[2]))
                self.charging_rate.append(float(_l[3]))
                self.discharging_rate.append(float(_l[4]))
                self.max_battery.append(float(_l[5]))
                self.speed.append(float(_l[6]))

            _input_file.close()
        
        self._df["Sr"] = self.source_node
        self._df["Dr"] = self.destination_node
        self._df["Br"] = self.initial_battery
        self._df["cr"] = self.charging_rate
        self._df["dr"] = self.discharging_rate
        self._df["Mr"] = self.max_battery
        self._df["sr"] = self.speed

        self.current_node = copy.deepcopy(self.source_node)

    def make_graphs(self):
        if self.graph_made:
            return
        for i in range(self.k):
            G = nx.Graph()
            for edg in self.edge_list:
                if self.battery_to_travel(i,edg) > self.max_battery[i]:
                    continue
                G.add_edge(edg[0],edg[1],weight=self.time_to_travel(i,edg))
            self.Graphs.append(G)
        self.graph_made = True
        return

    def theoritical_minima(self):
        """
        returns theoritical minimum time for all EVs to reach the destination
        """
        traveling_time = []
        charging_time = []
        total_time = []
        for i in range(self.k):
            spath = nx.shortest_path(self.Graphs[i],source=self.source_node[i],target=self.destination_node[i], weight='weight')
            print(spath)
            b = self.battery_usage_on_path(i,spath)
            traveling_time.append(b/self.discharging_rate[i])
            charging_time.append(max(b-self.initial_battery[i],0)/self.charging_rate[i])
            total_time.append(traveling_time[-1]+charging_time[-1])

        return np.max(np.array(total_time))

