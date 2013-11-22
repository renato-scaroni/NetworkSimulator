from operator import itemgetter

class EP3Simulator(object):
	def __init__(self, entities):
		self.entities = entities
		self.commands = []
		self.clock = 0

	def SetCommands(self, c): # a command is a tuple (time, commandString)
		self.commands = c

	def Simulate(self, outputFile):
		if len(self.commands) > 0:
			self.commands = sorted(self.commands, key=itemgetter(0))
			print "commands to execute :"
			for c in self.commands:
				print c

		keepSimulating = True
		while keepSimulating and len(self.commands) > 0:
			for c in self.commands:
				if c > self.clock:
					pass # Execute the little bastard

			keepSimulating = False
			for k in self.entities.keys():
				keepSimulating = self.entities[k].Loop() or keepSimulating
				self.entities[k].PrintLinks()
			self.clock += 0.001
		
class Agent(object):
	def __init__(self, name):
		pass	

class Sniffer(Agent):
	def __init__(self, name):
		print "sniffer criado ", name

	def SetLogFile(self, path):
		print name, "log salvo em", path
		self.logPath = path

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
		self.sniffer = None
		self.packets = []

	def SetSniffer(self, s):
		if self.destinationPort == -1:
			print "sniffer no link para", self.destinationName
		else:
			print "sniffer no link para", str(self.destinationName)+ "." +str(self.destinationPort)
		self.sniffer = s

	def SetSpeed(self, s):
		self.speed = s

	def SetDelay (self, d):
		self.delay = d

	def SetDestination(self, d, p):
		self.destinationName = d
		self.destinationPort = p #if its not a router, it should be -1

# May also be refered to as a device. Its an abstraction
# for both Host and Router
class Entity(object): 
	def __init__(self, name):
		self._type = type(self)
		Entity.host = type(Host("")) #save the type of a host for future consultation
		Entity.router = type(Router("", -1))#save the type of a router for future consultation
		self.agents = {}
		pass

	def Loop():
		pass

	def GetType(self):
		return self._type

	def AttachAgent(self, agName, ag):
		print agName, "associado a", self._name
		self.agents[agName]  = ag

class Host(Entity):
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
		return len(self.link.packets) > 0

	def SetLink(self, d, s, dest, destp):
		newLink = Link()

		newLink.SetSpeed(s)
		newLink.SetDelay(d)
		newLink.SetDestination(dest, destp)

		self.link = newLink

	def SetIps(self, host, router, dns):
		self.me = host
		self.router = router
		self.dns = dns[:-1]
		print "\n", self._name, ":"
		print "ip", self.me
		print "router", router
		print "DNS:", dns[:-1], "\n"

	def GetLink(self):
		return self.link

	def PrintLinks(self):
		if not self.link.destinationPort == -1:
			print self._name, "-->", str(self.link.destinationName)+"."+str(self.link.destinationPort), str(self.link.speed)+"ms", str(self.link.delay)+ "Mbps"
		else:
			print self._name, "-->", self.link.destinationName, str(self.link.speed)+"ms", str(self.link.delay), "Mbps"

class Router(Entity):
	def __init__(self):
		pass

	def __init__(self, name, interfacesCount):
		if interfacesCount == -1:
			return
		Entity.__init__(self, name)
		self.interfacesCount = interfacesCount
		
		self.links = [] #create dummy links
		#List that will contain the max packet each interface
		#can handle 
		self.maxPacketQueue = [] 
		#initialize the lists
		for i in range (interfacesCount):
			self.links.append(Link())
			self.maxPacketQueue.append(0)
		
		print "Router criado ", name
		
		self._name = name

		#this list will keep tuples with the ports and ips 
		#that will indentify this router
		self.ips = [] 

		#this dict will keep the routes table
		self.routes = {}

		#time consumed by the router to process 1 packet
		self.procTime = 0

	def SetRoutes(self, orig, dest):
		self.routes[orig] = dest

	def SetLink(self, d, s, dest, destp, port):
		if port > self.interfacesCount:
			print "porta inexistente"
			return
 
		self.links[port].SetSpeed(s)
		self.links[port].SetDelay(d)
		self.links[port].SetDestination(dest, destp)

	def SetIps(self, ip, port):
		self.ips.append((ip, port))
		print "orig", ip
		print "dest", port, "\n"

	def SetProcTime(self, p):
		print "Tempo de processamento de pacotes", p
		self.procTime = p

	def SetMaxQueueForPort(self, port, l):		
		self.maxPacketQueue[port] = l
		print "porta", port
		print "limite", l, "\n"

	def GetLink(self, port):
		return self.links[int(port)]

	def PrintLinks(self):
		for i in range(self.interfacesCount):
			l = self.links[i]
			if not l.destinationPort == -1:
				print self._name+"."+str(i), "-->", str(l.destinationName) + "."+ str(l.destinationPort), str(l.speed)+"ms", str(l.delay)+ "Mbps"
			else:
				print self._name+"."+str(i), "-->", l.destinationName, str(l.speed)+"ms", str(l.delay)+ "Mbps"

	def Loop(self):
		print "executando router ", self._name
		for l in self.links:
			if len(l.packets) > 0: return True
		return False