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
		self.destinationName = None
		self.destinationPort = -1

	def SetSpeed(self, s):
		self.speed = s

	def SetDelay (self, d):
		self.delay = d

	def SetDestination(self, d, p):
		self.destinationName = d
		self.destinationPort = p #if its not a router, it should be -1

class Entity(object):
	_sniffer = None
	def __init__(self, name):
		self._type = type(self)
		Entity.host = type(Host("")) #save the type of a host for future consultation
		Entity.router = type(Router("", -1))#save the type of a router for future consultation
		pass

	def Loop():
		pass

	def GetType(self):
		return self._type

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

	def SetIps(self, host, router, dns):
		self.me = host
		self.router = router
		self.dns = dns[:-1]
		print "\n", self._name, ":"
		print "ip", self.me
		print "router", router
		print "DNS:", dns[:-1], "\n"

	def PrintLinks(self):		
		if not self.links.destinationPort == -1:
			print self._name, "-->", str(self.links.destinationName)+"."+str(self.links.destinationPort), self.links.speed, "ms", self.links.delay, "Mbps"
		else:
			print self._name, "-->", self.links.destinationName, self.links.speed, "ms", self.links.delay, "Mbps"

class Router(Entity):
	def __init__(self):
		pass

	def __init__(self, name, interfacesCount):
		if interfacesCount == -1:
			return
		Entity.__init__(self, name)
		self.interfacesCount = interfacesCount
		
		#create dummy links and initialize them
		self.links = []
		for i in range (interfacesCount):
			self.links.append(Link())
		
		print "Router criado ", name
		
		self._name = name

		#this list will keep tuples with the ports and ips 
		#that will indentify this router
		self.ips = [] 

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
				print self._name+"."+str(i), "-->", str(l.destinationName) + "."+ str(l.destinationPort), l.speed, "ms", l.delay, "Mbps"
			else:
				print self._name+"."+str(i), "-->", l.destinationName, l.speed, "ms", l.delay, "Mbps"

	def SetIps(self, ip, port):
		self.ips.append((ip, port))

	def Loop(self):
		print "executando router ", self._name