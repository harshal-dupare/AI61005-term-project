import networkx as nx
from queue import PriorityQueue
import copy

global EVs
global Graph_of_cities
global shortest_path_length
global shortest_paths
global smallest_time_for_next_event
global node_counter
global n
global r

def shortest_path_between_each_city():

	global EVs
	global Graph_of_cities
	global shortest_path_length
	global shortest_paths
	shortest_paths, shortest_path_length = nx.floyd_warshall_predecessor_and_distance(Graph_of_cities,weight='weight')

class node:

	def __init__(self, node_number, parent_number, state_of_EVs, state_of_charging_stations, time, cost):

		self.node_number = node_number
		self.parent_number = parent_number
		#EV:[(previous city,time of leaving), (current city,time of arrival), (next city, expected time of arrival), 
		#charging status, amount of charge at current time, required amount of charge to reach destination on current path,
		#(best time from current city, priority)]
		self.state_of_EVs = state_of_EVs						
		self.state_of_charging_stations = state_of_charging_stations
		self.time = time
		self.cost = cost

	def moving_to_waiting_for_charging (self, EV):
		
		global EVs
		global Graph_of_cities
		global shortest_path_length
		time_of_event = self.state_of_EVs[EV][2][1]
		if time_of_event > smallest_time_for_next_event:
			return -1, []

		current_amount_of_charge = self.state_of_EVs[EV][4] - (time_of_event - self.time)*EVs[EV][6]/EVs[EV][4]
		required_amount_of_charge_to_reach_destination = shortest_path_length[self.state_of_EVs[EV][2][0]] [EVs[EV][1]] / EVs[EV][4]
		event = copy.deepcopy(self.state_of_EVs[EV])
		event[1] = list(event[2])
		event[2][0], event[2][1] = None, None
		event[4] = current_amount_of_charge
		event[5] = required_amount_of_charge_to_reach_destination
		event[6][0] = shortest_path_length[self.state_of_EVs[EV][2][0]] [EVs[EV][1]]/EVs[EV][6] + (required_amount_of_charge_to_reach_destination - current_amount_of_charge)/EVs[EV][3]
		EV_occupying_current_charging_station = self.state_of_charging_stations[self.state_of_EVs[EV][2][0]][1]
		if EV_occupying_current_charging_station != None:
			if (time_of_event + event[6][0]) <= (self.state_of_EVs[EV_occupying_current_charging_station][6][0] + self.time):
				event[6][1] = -1
			else:
				event[6][1] = 1
		return time_of_event , event
	
	def moving_to_moving (self, EV):

		global EVs
		global Graph_of_cities
		global shortest_path_length
		events = []
		time_of_event = self.state_of_EVs[EV][2][1]
		if time_of_event > smallest_time_for_next_event:
			return -1, []

		adjacent_cities = list(Graph_of_cities.adj[self.state_of_EVs[EV][2][0]])
		current_amount_of_charge = self.state_of_EVs[EV][4] - (time_of_event - self.time)*EVs[EV][6]/EVs[EV][4]
		for city in adjacent_cities:
			miniumum_charge_required_to_reach_the_city = Graph_of_cities[self.state_of_EVs[EV][2][0]][city]["weight"] / EVs[EV][4]
			if miniumum_charge_required_to_reach_the_city <= current_amount_of_charge:
				required_amount_of_charge_to_reach_destination = miniumum_charge_required_to_reach_the_city + shortest_path_length[city] [EVs[EV][1]] / EVs[EV][4]
				event = copy.deepcopy(self.state_of_EVs[EV])
				event[0] = list(event[2])
				event[2][0] = city
				event[2][1] = time_of_event + Graph_of_cities[self.state_of_EVs[EV][2][0]][city]["weight"] / EVs[EV][6]
				event[4] = current_amount_of_charge
				event[5] = required_amount_of_charge_to_reach_destination
				event[6][0] = ( Graph_of_cities[self.state_of_EVs[EV][2][0]][city]["weight"] + shortest_path_length[city] [EVs[EV][1]])/EVs[EV][6] + (required_amount_of_charge_to_reach_destination - current_amount_of_charge)/EVs[EV][3]
				events.append(event)

		return time_of_event , events

	def waiting_for_charging_to_charging (self, EV):

		global EVs
		global Graph_of_cities
		global shortest_path_length
		time_of_event = self.time
		current_city = self.state_of_EVs[EV][1][0]
		events = []
		event = copy.deepcopy(self.state_of_EVs[EV])
		if self.state_of_charging_stations[current_city][0] == 1:
			return -1, []
		else:
			event[6][1] = 1
			for other_EV in self.state_of_EVs:
				if other_EV == EV:
					continue
				else:
					if self.state_of_EVs[other_EV][1][0] == current_city:
						if (self.state_of_EVs[other_EV][6][0] + self.time) > (event[6][0] + self.time):
							event[6][1] = -1

			if event[6][1] == 1:
				event[3] = 1
				events.append(event)
		return time_of_event, events

	def charging_to_waiting_for_charging (self, EV):

		global EVs
		global Graph_of_cities
		global shortest_path_length
		time_of_event = self.time
		current_city = self.state_of_EVs[EV][1][0]
		events = []
		event = copy.deepcopy(self.state_of_EVs[EV])
		if self.state_of_EVs[EV][3] == 0:
			return -1, []
		else:
			for other_EV in self.state_of_EVs:
				if other_EV == EV:
					continue
				else:
					if self.state_of_EVs[other_EV][1][0] == current_city and self.state_of_EVs[other_EV][6][1] == 1:
						if (self.state_of_EVs[other_EV][6][0] + self.time) > (event[6][0] + self.time):
							event[6][1] = -1

			if event[6][1] == -1:
				event[3] = 0
				event[4] = self.state_of_EVs[EV][4] + (time_of_event - self.time)/EVs[EV][3]
				event[6][0] = shortest_path_length[self.state_of_EVs[EV][1][0]] [EVs[EV][1]]/EVs[EV][6] + (event[5] - event[4])/EVs[EV][3]
				events.append(event)
		return time_of_event, events

	def charging_to_moving (self, EV):

		global EVs
		global Graph_of_cities
		global shortest_path_length

		#5 cases 
		#1-forced to move when other vehicle with worse time arrives
		#2-moves when a new adjacent city becomes accessible
		#3-all adjacent cities are accessible but not fully charged, and a car in row for charging becomes worse than the current car
		#4-moves when it is fully charged
		#5-when it is charged enough to reach the destination
		#the 2nd case also provides for the case where the opposite happens, the vehicle keeps charging
		if self.state_of_EVs[EV][3] == 0:
			return -1, [], -1

		time_for_which_vehicle_is_charged = 0
		#case 1
		time_of_worse_incoming_EV = 1000000000000
		smallest_time_at_which_an_EV_becomes_worse = 1000000000000
		for other_EV in self.state_of_EVs:
				if other_EV == EV:
					continue
				else:
					if self.state_of_EVs[other_EV][1][0] == self.state_of_EVs[EV][1][0]:
						time_at_which_other_EV_becomes_worse = self.time + self.state_of_EVs[EV][6][0] - self.state_of_EVs[other_EV][6][0]
						if time_at_which_other_EV_becomes_worse < smallest_time_at_which_an_EV_becomes_worse:
							smallest_time_at_which_an_EV_becomes_worse = time_at_which_other_EV_becomes_worse
						if (self.state_of_EVs[other_EV][6][0] + self.time) > (self.state_of_EVs[EV][6][0] + self.time):
							if self.state_of_EVs[other_EV][6][1] == 1:
								time_of_worse_incoming_EV = self.time			
		time_of_event, case = time_of_worse_incoming_EV, 1 

		#case 2
		adjacent_cities = list(Graph_of_cities.adj[self.state_of_EVs[EV][1][0]])
		reachable_cities_with_current_charge = []
		next_city_which_is_accessible = [[], 1000000000000]
		last_city_which_is_accessible = [[], -1]
		for city in adjacent_cities:
			miniumum_charge_required_to_reach_the_city = Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][4]
			if miniumum_charge_required_to_reach_the_city <=self.state_of_EVs[EV][4]:
				reachable_cities_with_current_charge.append(city)
			else:
				time_when_city_is_reachable = self.time + (miniumum_charge_required_to_reach_the_city - self.state_of_EVs[EV][4])/EVs[EV][3]
				if time_when_city_is_reachable < next_city_which_is_accessible[1]:
					next_city_which_is_accessible[0] = [city]
					next_city_which_is_accessible[1] = time_when_city_is_reachable
				elif time_when_city_is_reachable == next_city_which_is_accessible[1]:
					next_city_which_is_accessible[0].append(city)
					next_city_which_is_accessible[1] = time_when_city_is_reachable
				elif time_when_city_is_reachable > last_city_which_is_accessible[1]:
					last_city_which_is_accessible = [[city], time_when_city_is_reachable]
		if next_city_which_is_accessible[1] < time_of_event:
			time_for_which_vehicle_is_charged = (Graph_of_cities[self.state_of_EVs[EV][1][0]][next_city_which_is_accessible[0][0]]["weight"] / EVs[EV][4] - self.state_of_EVs[EV][4])/EVs[EV][3]
			time_of_event, case = next_city_which_is_accessible[1], 2
			reachable_cities_with_current_charge = reachable_cities_with_current_charge + next_city_which_is_accessible[0]

		#case 3
		time_when_forced_to_move_by_waiting_cars = 1000000000000
		if next_city_which_is_accessible[0] == last_city_which_is_accessible[0]:
			if smallest_time_at_which_an_EV_becomes_worse >= last_city_which_is_accessible[1] and smallest_time_at_which_an_EV_becomes_worse >= self.time:
				time_when_forced_to_move_by_waiting_cars = smallest_time_at_which_an_EV_becomes_worse
			else:
				if last_city_which_is_accessible[1] != -1:
					time_when_forced_to_move_by_waiting_cars = last_city_which_is_accessible[1]
				else:
					time_when_forced_to_move_by_waiting_cars = self.time
		if time_when_forced_to_move_by_waiting_cars < time_of_event:
			if time_for_which_vehicle_is_charged == 0:
				time_for_which_vehicle_is_charged = time_when_forced_to_move_by_waiting_cars - self.time
			time_of_event, case = time_when_forced_to_move_by_waiting_cars, 3

		#case 4
		time_when_EV_is_fully_charged = self.time + (EVs[EV][5]-self.state_of_EVs[EV][4])/EVs[EV][3]
		if time_when_EV_is_fully_charged <= time_of_event:
			time_for_which_vehicle_is_charged = (EVs[EV][5]-self.state_of_EVs[EV][4])/EVs[EV][3]
			reachable_cities_with_current_charge = adjacent_cities
			time_of_event, case = time_when_EV_is_fully_charged, 4

		#case 5
		##If this case occurs, EV will head for its destination, without any stops
		if self.state_of_EVs[EV][5] > EVs[EV][5]:
			time_when_destination_node_is_reachable = 1000000000000
		else:
			time_when_destination_node_is_reachable = self.time +((self.state_of_EVs[EV][5] - self.state_of_EVs[EV][4]))/EVs[EV][3]
		if time_when_destination_node_is_reachable <= time_of_event:
			time_of_event, case = time_when_destination_node_is_reachable, 5

		if time_of_event > smallest_time_for_next_event:
			return -1, [], -1
		events = []
		amount_of_charge_when_the_EV_moves = self.state_of_EVs[EV][4] + time_for_which_vehicle_is_charged*EVs[EV][3]
		if case!=5:
			for city in reachable_cities_with_current_charge:
				miniumum_charge_required_to_reach_the_city = Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][4]
				if miniumum_charge_required_to_reach_the_city <= amount_of_charge_when_the_EV_moves:
					required_amount_of_charge_to_reach_destination = miniumum_charge_required_to_reach_the_city + shortest_path_length[city] [EVs[EV][1]] / EVs[EV][4]
					event = copy.deepcopy(self.state_of_EVs[EV])
					event[0] = [event[1][0], time_of_event]
					event[1][0] = None
					event[1][1] = None
					event[2][0] = city
					event[2][1] = time_of_event + Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][6]
					event[3] = 0
					event[4] = amount_of_charge_when_the_EV_moves
					event[5] = required_amount_of_charge_to_reach_destination
					event[6][0] = (Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] + shortest_path_length[city] [EVs[EV][1]])/EVs[EV][6] + (required_amount_of_charge_to_reach_destination - amount_of_charge_when_the_EV_moves)/EVs[EV][3]
					event[6][1] = -1
					events.append(event)
		if case == 1:
			if time_of_event == next_city_which_is_accessible[1]:
				return -1, [], -1

			return time_of_event, events, 1

		if case == 2:
			event = copy.deepcopy(self.state_of_EVs[EV])
			event[3] = 1
			event[4] = amount_of_charge_when_the_EV_moves
			event[6][0] = shortest_path_length[self.state_of_EVs[EV][1][0]] [EVs[EV][1]]/EVs[EV][6] + (event[5] - amount_of_charge_when_the_EV_moves)/EVs[EV][3]
			event[6][1] = 1
			events.append(event)
			return time_of_event, events, 2

		if case == 3:
			return time_of_event, events, 3

		if case == 4:
			return time_of_event, events, 4

		if case == 5:
			time, events = self.on_path_to_destination(EV, time_of_event)
			return time_of_event, events, 5

	def starting_from_source(self,EV):

		adjacent_cities = list(Graph_of_cities.adj[self.state_of_EVs[EV][1][0]])
		reachable_cities_with_current_charge = []
		for city in adjacent_cities:
			miniumum_charge_required_to_reach_the_city = Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][4]
			if miniumum_charge_required_to_reach_the_city <= self.state_of_EVs[EV][4]:
				reachable_cities_with_current_charge.append(city)
			
		time_of_event = self.time
		events = []
		amount_of_charge_when_the_EV_moves = self.state_of_EVs[EV][4] + (time_of_event - self.time)*EVs[EV][3]
		for city in reachable_cities_with_current_charge:
			miniumum_charge_required_to_reach_the_city = Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][4]
			if miniumum_charge_required_to_reach_the_city <= amount_of_charge_when_the_EV_moves:
				required_amount_of_charge_to_reach_destination = miniumum_charge_required_to_reach_the_city + shortest_path_length[city] [EVs[EV][1]] / EVs[EV][4]
				event = copy.deepcopy(self.state_of_EVs[EV])
				event[0] = list(event[1])
				event[1][0] = None
				event[1][1] = None
				event[2][0] = city
				event[2][1] = time_of_event + Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] / EVs[EV][6]
				event[3] = 0
				event[4] = amount_of_charge_when_the_EV_moves
				event[5] = required_amount_of_charge_to_reach_destination
				event[6][0] = (Graph_of_cities[self.state_of_EVs[EV][1][0]][city]["weight"] + shortest_path_length[city] [EVs[EV][1]])/EVs[EV][6] + (required_amount_of_charge_to_reach_destination - amount_of_charge_when_the_EV_moves)/EVs[EV][3]
				event[6][1] = -1
				events.append(event)

		if self.state_of_EVs[EV][4] < EVs[EV][5] :
			event = copy.deepcopy(self.state_of_EVs[EV])
			events.append(event)
			return time_of_event, events

	def on_path_to_destination(self, EV, time_of_event):

		global EVs
		global Graph_of_cities
		global shortest_path_length
		global shortest_paths

		if self.state_of_EVs[EV][1][0] != None:
			current_city = self.state_of_EVs[EV][1][0]
		else:
			current_city = self.state_of_EVs[EV][2][0]
			time_of_event = self.state_of_EVs[EV][2][1]

		if time_of_event > smallest_time_for_next_event:
			return -1, []

		if current_city == EVs[EV][1] and self.state_of_EVs[EV][0][0] == None:
			return -1, []

		events = []
		if current_city != EVs[EV][1]:
			path_to_destination = nx.reconstruct_path(current_city, EVs[EV][1], shortest_paths)
			next_city = path_to_destination[1]
			time_when_EV_reaches_next_city = time_of_event + Graph_of_cities[current_city][next_city]["weight"] / EVs[EV][6]
			charge_remaining_at_the_time_of_event = self.state_of_EVs[EV][4] - (time_of_event - self.time) * EVs[EV][6] / EVs[EV][4]
			event = copy.deepcopy(self.state_of_EVs[EV])
			event[0] = [current_city, time_of_event]
			event[1] = [None, None]
			event[2] = [next_city, time_when_EV_reaches_next_city]
			event[3] = 0
			event[4] = charge_remaining_at_the_time_of_event
			event[5] = shortest_path_length[current_city] [EVs[EV][1]] / EVs[EV][4]
			event[6][0] = shortest_path_length[current_city] [EVs[EV][1]]/EVs[EV][6]
			event[6][1] = -1
			events.append(event)
			return time_of_event, events


		if current_city == EVs[EV][1]:
			charge_remaining_at_the_time_of_event = self.state_of_EVs[EV][4] - (time_of_event - self.time) * EVs[EV][6] / EVs[EV][4]
			event = copy.deepcopy(self.state_of_EVs[EV])
			event[0] = [None, None]
			event[1] = [current_city, time_of_event]
			event[2] = [current_city, time_of_event]
			event[3] = 0
			event[4] = charge_remaining_at_the_time_of_event
			event[5] = 0
			event[6][0] = 0
			event[6][1] = -1
			events.append(event)
		return time_of_event, events


	def events(self):
		Events = []				#list of all events
		global smallest_time_for_next_event
		smallest_time_for_next_event = 1000000000000
		for EV in self.state_of_EVs:
			if self.node_number != 0:
				if self.state_of_EVs[EV][4]<self.state_of_EVs[EV][5]:

					if self.state_of_EVs[EV][1][0] == None:
						time_of_event, event = self.moving_to_waiting_for_charging (EV)
						if time_of_event != -1:
							Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
							if time_of_event <= smallest_time_for_next_event:
								smallest_time_for_next_event = time_of_event
						if smallest_time_for_next_event < self.time:
							return -1

						time_of_event, events = self.moving_to_moving (EV)
						if time_of_event != -1:
							if len(events) > 0:
								for event in events:
									Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
								if time_of_event <= smallest_time_for_next_event:
									smallest_time_for_next_event = time_of_event	
						if smallest_time_for_next_event < self.time:
							return -1

					else:
						if self.state_of_EVs[EV][3] == 0:

							time_of_event, events = self.waiting_for_charging_to_charging (EV)
							if time_of_event != -1:
								if len(events) > 0:
									for event in events:
										Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
									if time_of_event <= smallest_time_for_next_event:
										smallest_time_for_next_event = time_of_event
							if smallest_time_for_next_event < self.time:
								return -1

						else:

							time_of_event, events = self.charging_to_waiting_for_charging (EV)
							if time_of_event != -1:
								if len(events) > 0:
									for event in events:
										Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
									if time_of_event <= smallest_time_for_next_event:
										smallest_time_for_next_event = time_of_event
							if smallest_time_for_next_event < self.time:
								return -1

							time_of_event, events, case = self.charging_to_moving (EV)
							if time_of_event != -1:
								if len(events) > 0:
									for event in events:
										if event[3] == 0:
											Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
										elif event[3] == 1 and case == 2:
											Events.append([EV, time_of_event, event, None])
									if time_of_event <= smallest_time_for_next_event:
										smallest_time_for_next_event = time_of_event
							if smallest_time_for_next_event < self.time:
								return -1

				else:

					time_of_event, events = self.on_path_to_destination(EV, self.time)
					if time_of_event != -1:
						if len(events) > 0:
							for event in events:
								Events.append([EV, time_of_event, event, None])
							if time_of_event <= smallest_time_for_next_event:
								smallest_time_for_next_event = time_of_event
					if smallest_time_for_next_event < self.time:
						return -1
								
			else:
				if self.state_of_EVs[EV][4]<self.state_of_EVs[EV][5]:

					time_of_event, events = self.waiting_for_charging_to_charging (EV)
					if time_of_event != -1:
						if len(events) > 0:
							for event in events:
								Events.append([EV, time_of_event, event, self.state_of_EVs[EV][1][0]])
							if time_of_event <= smallest_time_for_next_event:
								smallest_time_for_next_event = time_of_event
					if smallest_time_for_next_event < self.time:
						return -1

					time_of_event, events = self.starting_from_source (EV)
					if time_of_event != -1:
						if len(events) > 0:
							for event in events:
								Events.append([EV, time_of_event, event, None])
							if time_of_event <= smallest_time_for_next_event:
								smallest_time_for_next_event = time_of_event
					if smallest_time_for_next_event < self.time:
						return -1

				else:

					time_of_event, events = self.on_path_to_destination(EV, self.time)
					if time_of_event != -1:
						if len(events) > 0:
							for event in events:
								Events.append([EV, time_of_event, event, None])
							if time_of_event <= smallest_time_for_next_event:
								smallest_time_for_next_event = time_of_event
					if smallest_time_for_next_event < self.time:
						return -1

		for Event in Events[:]:
			if Event[1] > smallest_time_for_next_event:
				Events.remove(Event)

		if smallest_time_for_next_event < self.time:
			return -1

		return Events

def all_possible_combination_of_Events(Events):

	time_of_transformation = Events[0][1]
	for Event in Events:
		if time_of_transformation != Event[1]:
			return -1, {}

	transformations = [{}]
	for Event in Events:
		new_transformations = []
		for transformation in transformations:
			need_to_create_new_transformation = False
			for key in transformation:
				if (key[1] !=None and Event[3] == key[1]) or Event[0] == key[0]:
					need_to_create_new_transformation = True
					break

				else:
					need_to_create_new_transformation = False

			if need_to_create_new_transformation:
				new_transformation = copy.copy(transformation)
				del new_transformation[key]
				new_transformation[(Event[0],Event[3])] = Event[2]
				if new_transformation not in  new_transformations:
					new_transformations.append(new_transformation)

			else:
				transformation[(Event[0],Event[3])] = Event[2]

		if len(new_transformations) > 0:
			for new_transformation in new_transformations:
				transformations.append(new_transformation)

	remove_duplicate = []
	for transformation in transformations:
		if transformation not in remove_duplicate:
			remove_duplicate.append(transformation)
	transformations = remove_duplicate

	return time_of_transformation, transformations

def A_star(): 

	global node_counter
	explored_node_counter = 0
	node_counter = 0
	q = PriorityQueue()
	explored_state_space = {}

	initial_time = 0
	initial_state_of_charging_stations = [[0, None]]*n
	initial_state_of_EVs = {}
	worst_best_time = -1

	for EV in EVs:
		initial_state_of_EV = []
		initial_state_of_EV.append([EVs[EV][0], 0])
		initial_state_of_EV.append([EVs[EV][0], 0])
		initial_state_of_EV.append([None, None])
		initial_state_of_EV.append(0)
		initial_state_of_EV.append(EVs[EV][2])

		charge_required_to_reach_destination = shortest_path_length[EVs[EV][0]][EVs[EV][1]]/EVs[EV][4]
		initial_state_of_EV.append(charge_required_to_reach_destination)
		if charge_required_to_reach_destination > EVs[EV][2]:
			best_time_for_EV = shortest_path_length[EVs[EV][0]][EVs[EV][1]]/EVs[EV][6] + (charge_required_to_reach_destination - EVs[EV][2])/EVs[EV][3]
		else:
			best_time_for_EV = shortest_path_length[EVs[EV][0]][EVs[EV][1]]/EVs[EV][6]
		initial_state_of_EV.append([best_time_for_EV, -1])

		if worst_best_time < best_time_for_EV:
			worst_best_time = best_time_for_EV
		initial_state_of_EVs[EV] = initial_state_of_EV

	cost = initial_time + worst_best_time

	source_node = node(node_counter, None, initial_state_of_EVs, initial_state_of_charging_stations, initial_time, cost )
	q.put((source_node.cost, source_node.node_number, source_node))
	node_counter = node_counter + 1
	wrong_transformation_counter = 0

	while not q.empty():

		queued_node = q.get()
		parent_node = queued_node[2]
		Events = parent_node.events()
		if Events == -1:
			print("There is problem in timing of events")
			break

		if len(Events) != 0:
			time_of_transformation, transformations = all_possible_combination_of_Events(Events)
			if time_of_transformation == -1:
				print("There is problem with creating Events")
				break

			for transformation in transformations:
				worst_best_time = -1
				child_node = copy.deepcopy(parent_node)
				wrong_transformation = False
				change_in_state_of_EV = [False]*r
				change_in_state_of_charging_station = [False]*n
				for event in transformation:
					if not change_in_state_of_EV[event[0]]:
						child_node.state_of_EVs[event[0]] = copy.deepcopy(transformation[event])
						change_in_state_of_EV[event[0]] = True
					else:
						wrong_transformation_counter = wrong_transformation_counter + 1
						wrong_transformation = True
						break

					if event[1] != None :
						if parent_node.state_of_charging_stations[event[1]][0] != transformation[event][3]:
							if not change_in_state_of_charging_station[event[1]]:
								child_node.state_of_charging_stations[event[1]][0] = transformation[event][3]
								if transformation[event][3] == 0:
									child_node.state_of_charging_stations[event[1]][1] = None
								else:
									child_node.state_of_charging_stations[event[1]][1] = event[0]
								change_in_state_of_charging_station[event[1]] = True
							else:
								wrong_transformation_counter
								wrong_transformation = True
								break
					best_time_for_EV = child_node.state_of_EVs[event[0]][6][0]
					if worst_best_time < best_time_for_EV:
						worst_best_time = best_time_for_EV

				if wrong_transformation:
					print("There is problem with creating transformation")
					continue

				for EV in range(0,r):
					if child_node.state_of_EVs[EV][1][0] != child_node.state_of_EVs[EV][2][0]:
						if not change_in_state_of_EV[EV]:
							if child_node.state_of_EVs[EV][1][0] != None:
								if child_node.state_of_EVs[EV][3] == 1:
									current_amount_of_charge = parent_node.state_of_EVs[EV][4] + (time_of_transformation - parent_node.time)*EVs[EV][3]
									child_node.state_of_EVs[EV][4] = current_amount_of_charge
									child_node.state_of_EVs[EV][6][0] = shortest_path_length[child_node.state_of_EVs[EV][1][0]] [EVs[EV][1]]/EVs[EV][6] + (child_node.state_of_EVs[EV][5] - current_amount_of_charge)/EVs[EV][3]
									best_time_for_EV = child_node.state_of_EVs[EV][6][0]
									if worst_best_time < best_time_for_EV:
										worst_best_time = best_time_for_EV

								else:
									best_time_for_EV = child_node.state_of_EVs[EV][6][0]
									if worst_best_time < best_time_for_EV:
										worst_best_time = best_time_for_EV

							else:
								current_amount_of_charge = parent_node.state_of_EVs[EV][4] - (time_of_transformation - parent_node.time)*EVs[EV][6]/EVs[EV][4]
								required_amount_of_charge_to_reach_destination = parent_node.state_of_EVs[EV][5] - (time_of_transformation - parent_node.time)*EVs[EV][6]/EVs[EV][4]
								child_node.state_of_EVs[EV][4] = current_amount_of_charge
								child_node.state_of_EVs[EV][5] = required_amount_of_charge_to_reach_destination
								child_node.state_of_EVs[EV][6][0] = parent_node.state_of_EVs[EV][6][0] - (time_of_transformation - parent_node.time)
								best_time_for_EV = child_node.state_of_EVs[EV][6][0]
								if worst_best_time < best_time_for_EV:
									worst_best_time = best_time_for_EV

				child_node.node_number = node_counter
				child_node.parent_number = parent_node.node_number
				child_node.time = time_of_transformation
				child_node.cost = time_of_transformation + worst_best_time
				q.put((child_node.cost, child_node.node_number, child_node))
				node_counter = node_counter + 1

		if len(Events) == 0:
			destination_node = parent_node
			print("Required state has been reached!")
			print("Time when last EV reaches its destionation is ", parent_node.time)
			break

		explored_state_space[parent_node.node_number] = parent_node
		explored_node_counter = explored_node_counter +1

		##choose according to the resources available in your computer
		if node_counter >= 100000:
			print("Too many nodes explored")
			break

def input():

	global EVs
	global Graph_of_cities
	global r
	global n
	Graph_of_cities = nx.Graph()
	n = r = 0
	EVs = {}

	#enter your input file name here, note that the form of input must be same as that of provided in examples
	input_file = open("map.txt","r")

	number_of_line_with_single_number = 0
	EV_counter = 0
	for line in input_file:
		number = 0
		number_of_numbers_in_line =0
		data = []
		decimal = False
		position_after_decimal = 0

		for character in line:
			if character.isdigit():
				number = number*(int(decimal)) + number*10*(1 - int(decimal)) + int(character)/(10**(position_after_decimal))
				position_after_decimal = position_after_decimal + 1*(int(decimal))
			else:
				if character == ".":
					decimal = True
					position_after_decimal = position_after_decimal + 1*(int(decimal))
				else:
					number_of_numbers_in_line = number_of_numbers_in_line + 1
					if number_of_numbers_in_line <=2:
						number = int(number)
					data.append(number)
					number = 0
					decimal = False
					position_after_decimal = 0
					
		if number_of_numbers_in_line == 1:
			number_of_line_with_single_number = number_of_line_with_single_number + 1

		if number_of_numbers_in_line == 1 and number_of_line_with_single_number == 1:
			n = data[0]
		elif number_of_numbers_in_line == 3 and number_of_line_with_single_number == 2:
			Graph_of_cities.add_edge(data[0], data[1], weight = data[2])
		elif number_of_numbers_in_line == 1 and number_of_line_with_single_number == 3:
			r = data[0]
		elif number_of_numbers_in_line == 7 and number_of_line_with_single_number == 3:
			EVs[EV_counter] = data
			EV_counter = EV_counter + 1


	shortest_path_between_each_city()

	A_star()

if __name__ == "__main__":

	input()
