import simpy
import random

RANDOM_SEED = 42

NUM_ATENDENTES = 5		
NUM_AUTO_MACHINES = 5
NUM_SECURITY = 7
NUM_GATES = 3
NUM_IMMIGRATIONS = 6
NUM_CUSTOMS = 4
NUM_LUGGAGE = 2

# Parametros usados para Retirada de bagagem
MTLS = 142.0
MEAN_LUGGAGE_TIME = 1 / MTLS
MEAN_LUGGAGE = 18.0
DELTA_LUGGAGE = 2.0

# Parametros usados para Alfandega
MTCF = 78.0
MEAN_CUSTOMS_FAILURE = 1 / MTCF
CUSTOM_MEAN = 32.0
CUSTOM_DELTA = 9.0

# Parametros usados para Imigração
MTIF = 592.0
MEAN_IMMIGRATION_FAILURE = 1 / MTIF
IMMIGRATION_MEAN = 46.0
IMMIGRATION_DELTA = 8.0

# Parametros usados para Avião
MTPF = 458.0
MEAN_PLANE_FAILURE = 1 / MTPF
MEAN_BOARDING = 13.0
BOARDING_DELTA = 3.0

# Parametros usados para checagem de segurança
PASSENGER_MEAN_TIME = 30.0
PASSENGER_DELTA = 6.0
MTTS = 270.0							# Mean time to security failure
MEAN_SECURITY_FAILURE = 1 / MTTS

REPAIR_EXTRAVIATION_PROBLEM = 27.0		# Time it takes to repair a extraviation in minutes
REPAIR_CUSTOM_PROBLEM = 18.0			# Time it takes to repair a custom in minutes
REPAIR_PLANE_PROBLEM = 230.0			# Time it takes to repair a plane in minutes
REPAIR_SECURITY_PROBLEM = 100.0			# Time it takes to repair a security checking in minutes
REPAIR_MACHINE_TIME = 30.0				# Time it takes to repair a machine in minutes
REPAIR_ATTENDANT_PROBLEM = 15.0			# Time it takes to repair a attendant problem in minutes

# Parametros usados para os atendimentos
PT_MEAN = 10.0         					# Avg. processing time in minutes
PT_SIGMA = 2.0        					# Sigma of processing time computers
MTTF = 300.0							# Mean Attendant time to failure in minutes
MEAN = 1 / MTTF							# Repair time

WEEKS = 4								# Time the simulation took
SIM_TIME = WEEKS * 7 * 24 * 60  		# Simulation time in Minutes

def time_to_luggage_extraviation():
	return random.expovariate(MEAN_LUGGAGE_TIME)

def passenger_luggage_time():
	return random.normalvariate(MEAN_LUGGAGE, DELTA_LUGGAGE)
	
class Baggage(object):
	def __init__(self, env, name):
		self.env = env
		self.name = name
		self.extraviated = False
		self.passengers_passed = 0
	
		self.process = env.process(self.running())
		env.process(self.extraviate())
	
	def running(self):
		while True:
			done_in = passenger_luggage_time()
			while done_in:
				try:
					start = self.env.now
					yield self.env.timeout(done_in)
					done_in = 0
				except simpy.Interrupt:
					self.extraviated = True
					done_in -= self.env.now - start
					yield self.env.timeout(REPAIR_EXTRAVIATION_PROBLEM)
					self.extraviated = False
			self.passengers_passed += 1
	
	def extraviate(self):
		while True:
			yield self.env.timeout(time_to_luggage_extraviation())
			if not self.extraviated:
				self.process.interrupt()

def time_to_immigration_failure():
	return random.expovariate(MEAN_IMMIGRATION_FAILURE)

def passenger_immigration_time():
	return random.normalvariate(IMMIGRATION_MEAN, IMMIGRATION_DELTA)
	
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
	return random.expovariate(MEAN_CUSTOMS_FAILURE)

def passenger_custom_time():
	return random.normalvariate(CUSTOM_MEAN, CUSTOM_DELTA)
	
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
	return random.expovariate(MEAN_PLANE_FAILURE)

def passenger_boarding_time():
	return random.normalvariate(MEAN_BOARDING, BOARDING_DELTA)
	
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
	return random.expovariate(MEAN_SECURITY_FAILURE)

def passenger_time():
	return random.normalvariate(PASSENGER_MEAN_TIME, PASSENGER_DELTA)
	
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
print('Aeroporto')
random.seed(RANDOM_SEED)

# Create an environment and start the setup process
env = simpy.Environment()

machines = [Machine(env, 'Auto Atendimento %d' % (i+1)) for i in range(NUM_AUTO_MACHINES)]
attendants = [Atendente(env, 'Atendente %d' % (i+1)) for i in range(NUM_ATENDENTES)]
securities = [Security(env, 'Checagem de Seguranca %d' % (i+1)) for i in range(NUM_SECURITY)]
planes = [Plane(env, 'Aviao %d' % (i+1)) for i in range(NUM_GATES)]
immigrations = [Immigration(env, 'Imigracao %d' % (i+1)) for i in range(NUM_IMMIGRATIONS)]
customs = [Custom(env, 'Anfandega %d' % (i+1)) for i in range(NUM_CUSTOMS)]
baggages = [Baggage(env, 'Retirada de Bagagem %d' % (i+1)) for i in range(NUM_LUGGAGE)]

# Executing
env.run(until=SIM_TIME)

# Results
print('Resultados do aeroporto depois de %d semanas\n' % WEEKS)
print('Auto Atendimentos: ')
for machine in machines:
    print('%s atendeu %d clientes.' % (machine.name, machine.clients_attended))
print

print('Atendentes: ')
for attendant in attendants:
    print('%s atendeu %d clientes.' % (attendant.name, attendant.clients_attended))
print

print('Checagens de seguranca: ')
for security in securities:
    print('%s revistou %d passageiros.' % (security.name, security.passengers_checked))
print

print('Avioes: ')
for plane in planes:
    print('%d passageiros embarcaram no %s.' % (plane.passengers_boarded, plane.name))
print

print('Imigracao: ')
for immigration in immigrations:
    print('%d passageiros passaram pela %s.' % (immigration.passengers_immigrated, immigration.name))
print

print('Alfandega: ')
for custom in customs:
    print('%d passageiros passaram pela %s.' % (custom.passengers_analized, custom.name))
print

print('Recepcao de Bagagem: ')
for bagagge in baggages:
    print('%d passageiros pegaram malas no %s.' % (bagagge.passengers_passed, bagagge.name))
#print('%s had %d passengers this month.' % (airport.name, airport.passengers_travelled))
