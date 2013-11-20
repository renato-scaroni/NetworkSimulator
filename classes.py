class EP3Simulator(object):
	def __init__(self, entities):
		self.entities = entities
		
	def simulate(self, outputFile):
		for k in self.entities.keys():
			self.entities[k].Loop()
			self.entities[k].PrintLinks()
		
class Agent(object):
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

class Link(object):
	def __init__(self):
		self.delay = -1
		self.speed = -1
		self.destinationHost = None
		self.destinationPort = -1
	def SetSpeed(self, s):
		self.speed = s
	def SetDelay (self, d):
		self.delay = d
	def SetDestination(self, d, p):
		self.destinationHost = d
		self.destinationPort = p

class Entity(object):
	_sniffer = None
	def __init__(self, name):
		pass

	def Loop():
		pass

class Host(Entity):
	links = None
	def __init__(self):
		pass
	def __init__(self, name):
		if(name == ""):
			return
		Entity.__init__(self, name)
		print "Host criado ", name
		self._name = name

	def Loop(self):
		print "executando host ", self._name

	def SetLink(self, d, s, dest, destp):
		newLink = Link()

		newLink.SetSpeed(s)
		newLink.SetDelay(d)
		newLink.SetDestination(dest, destp)

		self.links = newLink

	def PrintLinks(self):		
		if not self.links.destinationPort == -1:
			print self._name, "-->", str(self.links.destinationHost)+"."+str(self.links.destinationPort)
		else:
			print self._name, "-->", self.links.destinationHost

class Router(Entity):
	def __init__(self):
		pass

	def __init__(self, name, interfacesCount):
		Entity.__init__(self, name)
		self.interfacesCount = interfacesCount
		self.links = []
		for i in range (interfacesCount):
			self.links.append(Link())
		print "Router criado ", name
		self._name = name

	def SetLink(self, d, s, dest, destp, port):
		if port > self.interfacesCount:
			print "porta inexistente"
			return
 
		self.links[port].SetSpeed(s)
		self.links[port].SetDelay(d)
		self.links[port].SetDestination(dest, destp)

	def PrintLinks(self):
		for i in range(self.interfacesCount):
			l = self.links[i]
			if not l.destinationPort == -1:
				print self._name+"."+str(i), "-->", str(l.destinationHost) + "."+ str(l.destinationPort)
			else:
				print self._name+"."+str(i), "-->", l.destinationHost

	def Loop(self):
		print "executando router ", self._name