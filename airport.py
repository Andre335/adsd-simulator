import simpy
import random

RANDOM_SEED = 42
NUM_ATENDENTES = 5		
NUM_AUTO_MACHINES = 5
NUM_GATES = 2
REPAIR_AIRPORT_PROBLEM = 100.0			# Time it takes to repair a airport in minutes
REPAIR_MACHINE_TIME = 30.0				# Time it takes to repair a machine in minutes
REPAIR_ATTENDANT_PROBLEM = 15.0			# Time it takes to repair a attendant problem in minutes
PT_MEAN = 10.0         					# Avg. processing time in minutes
PT_SIGMA = 2.0        					# Sigma of processing time computers
MTTF = 300.0							# Mean Attendant time to failure in minutes
MEAN = 1 / MTTF							# Repair time
WEEKS = 4								# Time the simulation took
SIM_TIME = WEEKS * 7 * 24 * 60  		# Simulation time in Minutes

def airport(env, name, atendentes, buy_time, gate_time, board_time):
	print('%s buying ticket at %d' % (name, env.now))
	yield env.timeout(buy_time)
	
	print('%s waiting for travel day at %d' % (name, env.now))
	wait_for_travel_duration = 23
	yield env.timeout(wait_for_travel_duration)
	
	# Simulate going to airport
	going_to_airport = 30
	yield env.timeout(going_to_airport)
	
	print('%s ariving at airport at %d' % (name, env.now))
	ariving_at_airport = 2
	yield env.timeout(ariving_at_airport)

	with atendentes.request() as req:
		yield req
		
		print('%s checking in at %d' % (name, env.now))
		doing_check_in = 2
		yield env.timeout(doing_check_in)
		
		print('%s depatching baggage at %d' % (name, env.now))
		depatching_bags = 5
		yield env.timeout(depatching_bags)
		
		print('%s waiting until gate opens at %d' % (name, env.now))
		yield env.timeout(gate_time)
		
		print('%s security checking at %d' % (name, env.now))
		security_checking = 30
		yield env.timeout(security_checking)
		
		print('%s waiting until boarding time at %d' % (name, env.now))
		yield env.timeout(board_time)
		print('%s boarding at %d' % (name, env.now))

def time_to_airport_failure():
	return random.expovariate(MEAN)

def passenger_time():
	return random.normalvariate(PT_MEAN, PT_SIGMA)
	
class Airport(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.shutted = False
		self.passengers_travelled = 0
	
		self.process = env.process(self.running())
		env.process(self.shutdown())
	
	def running(self):
		while True:
			done_in = passenger_time()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.shutted = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_AIRPORT_PROBLEM)
					self.shutted = False
			self.passengers_travelled += 1
	
	def shutdown(self):
		while True:
			yield self.env.timeout(time_to_airport_failure())
			if not self.shutted:
				self.process.interrupt()

def attendant_time_per_atendimento():
    return random.normalvariate(PT_MEAN, PT_SIGMA)

def machine_time_per_atendimento():
    return random.normalvariate(PT_MEAN, PT_SIGMA)
	
def time_to_attendant_failure():
	return random.expovariate(MEAN)

def time_to_machine_failure():
	return random.expovariate(MEAN)
	
class Atendente(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.clients_attended = 0
		self.in_problem = False
		
		self.process = env.process(self.working())
		env.process(self.make_problem())
		
	def working(self):
		while True:
			done_in = attendant_time_per_atendimento()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.in_problem = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_ATTENDANT_PROBLEM)
					self.in_problem = False
			self.clients_attended += 1
	
	def make_problem(self):
		"""Some attendants have problems every now and then."""
		while True:
			yield self.env.timeout(time_to_attendant_failure())
			if not self.in_problem:
				# Only break the machine if it is currently working.
				self.process.interrupt()
	
class Machine(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.clients_attended = 0
		self.broken = False
		
		self.process = env.process(self.working())
		env.process(self.break_machine())
		
	def working(self):
		while True:
			done_in = machine_time_per_atendimento()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.broken = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_MACHINE_TIME)
					self.broken = False
			self.clients_attended += 1
	
	def break_machine(self):
		while True:
			yield self.env.timeout(time_to_machine_failure())
			if not self.broken:
				# Only break the machine if it is currently working.
				self.process.interrupt()
                
# Setting Up and Starting Simulation
print('Airport')
random.seed(RANDOM_SEED)

# Create an environment and start the setup process
env = simpy.Environment()
machines = [Machine(env, 'Machine %d' % (i+1))
            for i in range(NUM_AUTO_MACHINES)]
attendants = [Atendente(env, 'Atendente %d' % (i+1))
			for i in range(NUM_ATENDENTES)]
airport = Airport(env, 'Airport')

#for i in xrange(7):
#	env.process(airport(env, 'Passenger %d' % (i+1), atendentes, i*23, i*30, i*10))

# Executing
env.run(until=SIM_TIME)

# Results
print('Airport results after %d weeks' % WEEKS)
for machine in machines:
    print('%s attended %d clients.' % (machine.name, machine.clients_attended))

for attendant in attendants:
    print('%s attended %d clients.' % (attendant.name, attendant.clients_attended))
print('%s had %d passengers this month.' % (airport.name, airport.passengers_travelled))
