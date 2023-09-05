import queueing_tool as qt
import numpy as np
import math


current_cycle = 0 

#job de logging. 

#Arribo entre ciclo 0 y 60 -> 200 por segundo
#	entre ciclo 60 y 120 -> 400 por segundo
#	entre ciclo 120 y 240 -> 1000  por segundo
#	entre ciclo 240 y 300 -> 400 por segundo
#start servers 5
#service time 180ms

#ARRIVAL RATE. How many per time unit
def rate(t):
	if ( current_cycle <= 60):
		return 200
	if ( current_cycle <= 120):
		return 400 
	if ( current_cycle <= 240):
		return 1000 
	return 400 


def arr_f(t):
	return qt.poisson_random_measure(t,rate,rate(1))


def ser_f(t):
	res = t + np.random.exponential(0.180)
	return res


def avg_queue_lenght(data, initial):
	queue_index = 3
	l = list(data.values())[initial:]
	t = sum ( map(lambda x:x[0][queue_index], l )) *1.0/ len(l)
	return t 

def initial_last_queue_lenght(data, num_events):
	queue_index = 3
	l = list(map(lambda x:x[0][queue_index], data.values()))
	#print("DEBUG Get the last queue. %d" % len(l))
	#print("DEBUG Events. %d" % num_events)
	#print(l)
	return (l[0],l[-1])

def percentile_95_service_time(data, initial):
	arrival_time_index = 0
	departure_time_index = 2
	l = list(data.values())
	#print(l)
	#print(l[initial:])
	t = list(map ( lambda x:x[0][departure_time_index] - x[0][arrival_time_index], l[initial:]))
	t = sorted(filter(lambda x:x>0, t))
	if ( len(t) > 0 ):
		return np.percentile(t, 95)
	else:
		return -1

	
#If average last 5 queue measures > 1000 . Servers * 1.2 (ceiling )
#If average last 5 queue measures < 50. Servers * 0.8 ( min 2 )
def calculate_new_servers(last_queues, current_server_count):
	last_meas = 5
	upper_limit = 1000
	lower_limit = 100
	increment = 1.2
	new_server_count = current_server_count
	avg = sum(last_queues[-last_meas:]) / len(last_queues[-last_meas:])
	if ( avg > upper_limit ):
		new_server_count = math.ceil(current_server_count * increment)
	if ( avg < lower_limit ):
		new_server_count = math.floor(current_server_count / increment)
	return max(new_server_count ,2)
	

#Si los ultimos 3 crecen en más de un 10% respecto a los n-6 a n-3 y el average es > 1000,  aumenta servidores 1.2
#Si < 100 y derivada baja en 1.05
def calculate_new_servers_v2(last_queues, current_server_count):
	if ( len(last_queues) < 6) :
		return current_server_count

	increment = 1.2
	decrement = 1.05
	max_value = 1000
	absolute_max = 10000
	min_value = 100
	initial = current_server_count
	f = sum(last_queues[-6:-3]) *1.0
	l = sum(last_queues[-3:])*1.0
	#print("DEBUG. Last %f - Prev %f - Avg[-3] %f" % (l,f,l/3))
	if ( l / f > 1 and l/3 > max_value):
		current_server_count =  max(math.ceil(current_server_count * increment ),2)
	if ( l/3 < min_value and (f == 0 or  l/f < 0.9 )):
		current_server_count =  max(math.ceil(current_server_count / decrement ) ,2)
	print("DEBUG. Last %f - Prev %f - Coc %f - Avg[-3] %f - initial %d - current %d" % (l, f, l/max(f,1), l/3, initial,current_server_count))
	return current_server_count
		

def set_new_server_count(qn, new_server_count, cycle, server_target_cycle):
	delay = 2
	server_target_cycle[cycle+delay] = new_server_count
	current_server_count = server_target_cycle[cycle]
	qn.edge2queue[0].set_num_servers(current_server_count)
	print("DEBUG. Ciclo %d. Seteando %d servers para este ciclo. Seteando %d servers para ciclo %d" % (cycle, current_server_count,new_server_count, cycle+delay))


def simulate_control(qn,time_between_checks, cycles): 
	last_queues = []		
	qn.start_collecting_data()
	initial = 0 
	server_target_cycle = {}
	server_target_cycle[0] = qn.edge2queue[0].num_servers
	server_target_cycle[1] = qn.edge2queue[0].num_servers
	for i in range(0, cycles):
		current_cycle = i
		current_server_count = qn.edge2queue[0].num_servers

		qn.simulate( t= time_between_checks )

		data_out = qn.get_agent_data()
		queue_len = avg_queue_lenght(data_out,initial)
		initial_queue_len, last_queue_len = initial_last_queue_lenght(data_out, qn.num_events)
		percentile_95 = percentile_95_service_time(data_out, initial)
		
		last_queues.append(last_queue_len)
		new_server_count = calculate_new_servers_v2 ( last_queues, current_server_count )

		set_new_server_count( qn , new_server_count, i, server_target_cycle)

		print("Ciclo %d. Last queue %d. Average Queue %d. Service Time(95) %f.  Old Servers %d. New Servers %d" % (i, last_queue_len, queue_len, percentile_95, current_server_count , new_server_count))
		initial = len(data_out.values())
		print("Total de mediciones %d" % initial ) 
		#qn.clear_data()
	qn.stop_collecting_data()
		

#Pendientes
#3. ver como se cambian la cantidda de servers


q_classes = { 1: qt.QueueServer }
q_args = {
	1:{
		'num_servers': 5,
		'arrival_f': arr_f,
		'service_f': ser_f
	}
}  

adja_list = { 0:[1] }
edge_list = { 0:{1:1}}

g = qt.adjacency2graph( adjacency = adja_list, edge_type = edge_list )
qn = qt.QueueNetwork( g=g, q_classes = q_classes, q_args = q_args , max_agents = 10000000)
qn.initialize( edge_type = 1 )

simulate_control(qn,60, 400)

