class EP3Simulator:
	def __init__(self, entities):
		self.entities = entities
		
	def simulate(self, outputFile):
		print self.entities
		
class Agent:
	def __init__(self, name):
		pass	

class Sniffer(Agent):
	def __init__(self, name):
		print "sniffer criado ", name

class HttpClient(Agent):
	def __init__(self, name):
		print "Http Server criado ", name

class HttpServer(Agent):
	def __init__(self, name):
		print "Http Client criado ", name

class DNSServer(Agent):
	def __init__(self, name):
		print "DNS Server criado ", name

class Entity:
	sniffer = None
	def __init__(self, name):
		pass
	
class Host(Entity):
	def __init__(self, name):
		Entity.__init__(self, name)
	
class Router(Entity):
	def __init__(self, name, interfacesCount):
		Entity.__init__(self, name)
		self.interfacesCount = interfacesCount