import simpy
import random

RANDOM_SEED = 42
NUM_ATENDENTES = 5		
NUM_AUTO_MACHINES = 5
NUM_SECURITY = 7
NUM_GATES = 3
NUM_IMMIGRATIONS = 6
NUM_CUSTOMS = 4
REPAIR_CUSTOM_PROBLEM = 18.0			# Time it takes to repair a custom in minutes
REPAIR_PLANE_PROBLEM = 230.0			# Time it takes to repair a plane in minutes
REPAIR_SECURITY_PROBLEM = 100.0			# Time it takes to repair a security checking in minutes
REPAIR_MACHINE_TIME = 30.0				# Time it takes to repair a machine in minutes
REPAIR_ATTENDANT_PROBLEM = 15.0			# Time it takes to repair a attendant problem in minutes
PT_MEAN = 10.0         					# Avg. processing time in minutes
PT_SIGMA = 2.0        					# Sigma of processing time computers
MTTF = 300.0							# Mean Attendant time to failure in minutes
MEAN = 1 / MTTF							# Repair time
WEEKS = 4								# Time the simulation took
SIM_TIME = WEEKS * 7 * 24 * 60  		# Simulation time in Minutes

def time_to_immigration_failure():
	return random.expovariate(MEAN)

def passenger_immigration_time():
	return random.normalvariate(PT_MEAN, PT_SIGMA)
	
class Immigration(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.broken = False
		self.passengers_immigrated = 0
	
		self.process = env.process(self.running())
		env.process(self.broke())
	
	def running(self):
		while True:
			done_in = passenger_immigration_time()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.broken = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_CUSTOM_PROBLEM)
					self.broken = False
			self.passengers_immigrated += 1
	
	def broke(self):
		while True:
			yield self.env.timeout(time_to_immigration_failure())
			if not self.broken:
				self.process.interrupt()

def time_to_custom_failure():
	return random.expovariate(MEAN)

def passenger_custom_time():
	return random.normalvariate(PT_MEAN, PT_SIGMA)
	
class Custom(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.broken = False
		self.passengers_analized = 0
	
		self.process = env.process(self.running())
		env.process(self.broke())
	
	def running(self):
		while True:
			done_in = passenger_custom_time()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.broken = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_CUSTOM_PROBLEM)
					self.broken = False
			self.passengers_analized += 1
	
	def broke(self):
		while True:
			yield self.env.timeout(time_to_custom_failure())
			if not self.broken:
				self.process.interrupt()
				
def time_to_plane_failure():
	return random.expovariate(MEAN)

def passenger_boarding_time():
	return random.normalvariate(PT_MEAN, PT_SIGMA)
	
class Plane(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.closed = False
		self.passengers_boarded = 0
	
		self.process = env.process(self.running())
		env.process(self.close())
	
	def running(self):
		while True:
			done_in = passenger_boarding_time()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.closed = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_PLANE_PROBLEM)
					self.closed = False
			self.passengers_boarded += 1
	
	def close(self):
		while True:
			yield self.env.timeout(time_to_plane_failure())
			if not self.closed:
				self.process.interrupt()
				
def time_to_security_failure():
	return random.expovariate(MEAN)

def passenger_time():
	return random.normalvariate(PT_MEAN, PT_SIGMA)
	
class Security(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.shutted = False
		self.passengers_checked = 0
	
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
					yield self.env.timeout(REPAIR_SECURITY_PROBLEM)
					self.shutted = False
			self.passengers_checked += 1
	
	def shutdown(self):
		while True:
			yield self.env.timeout(time_to_security_failure())
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

machines = [Machine(env, 'Auto Atendimento %d' % (i+1))
            for i in range(NUM_AUTO_MACHINES)]
attendants = [Atendente(env, 'Atendente %d' % (i+1))
			for i in range(NUM_ATENDENTES)]
securities = [Security(env, 'Checagem de Seguranca %d' % (i+1))
			for i in range(NUM_SECURITY)]
planes = [Plane(env, 'Aviao %d' % (i+1)) for i in range(NUM_GATES)]
immigrations = [Immigration(env, 'Imigracao %d' % (i+1)) for i in range(NUM_IMMIGRATIONS)]
customs = [Custom(env, 'Anfandega %d' % (i+1)) for i in range(NUM_CUSTOMS)]

# Executing
env.run(until=SIM_TIME)

# Results
print('Airport results after %d weeks' % WEEKS)
for machine in machines:
    print('%s atendeu %d clientes.' % (machine.name, machine.clients_attended))

for attendant in attendants:
    print('%s atendeu %d clientes.' % (attendant.name, attendant.clients_attended))

for security in securities:
    print('%s checou %d passageiros.' % (security.name, security.passengers_checked))

for plane in planes:
    print('%d passageiros embarcaram no %s.' % (plane.passengers_boarded, plane.name))
    
for immigration in immigrations:
    print('%d passageiros passaram pela %s.' % (immigration.passengers_immigrated, immigration.name))

for custom in customs:
    print('%d passageiros passaram pela %s.' % (custom.passengers_analized, custom.name))
#print('%s had %d passengers this month.' % (airport.name, airport.passengers_travelled))
