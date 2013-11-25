from operator import itemgetter
import sys

simulatorSingleton = None
packetSize = 1024 * 8 * 500 #500 kbytes

class EP3Simulator(object):
	def __init__(self, entities, agents):
		global simulatorSingleton
		self.entities = entities
		self.agents = agents
		self.commands = []
		self.clock = 0
		simulatorSingleton = self

	def SetCommands(self, c): # a command is a tuple (time, commandString)
		self.commands = c

	def ParseAndExecuteCommand(self, cmd):
		print "Comando: " + cmd
		splittedCmd = cmd.replace("\"", "").replace("'", "").split(" ") #WTF???

		if cmd == "\"finish\"":
			return False

		agent = simulatorSingleton.agents[splittedCmd[0]]
		if agent.type == "httpc" and splittedCmd[1] == "GET":
			agent.Get(splittedCmd[2], self.entities)


		return True

	def Simulate(self, outputFile):
		if len(self.commands) > 0:
			self.commands = sorted(self.commands, key=itemgetter(0))
			print "commands to execute :"
			for c in self.commands:
				print c
			self.time = float(self.commands[0][0])
		else:
			print "Nao existem comandos a serem executados"
			return

		keepSimulating = True
		while keepSimulating or len(self.commands) > 0:
			for c in self.commands:
				if float(c[0]) < float(self.clock):
					if not self.ParseAndExecuteCommand(c[1]): self.commands = []
					else: self.commands = [s for s in self.commands if s != c]

			keepSimulating = False
			for k in self.entities.keys():
				keepSimulating = self.entities[k].Loop(self.entities) or keepSimulating
				# self.entities[k].PrintLinks()
			self.clock += 0.001

class Packet(object):
	def __init__(self):
		self.data = None
		self.header = None
		self.dataIsPacket = False

	def SetHeader(self, h):
		self.header = h

	def SetData(self, data, dataIsPacket):
		self.data = data
		self.dataIsPacket = dataIsPacket

class Header(object):
	def __init__(self):
		super(Header, self).__init__()

class UDPHeader(Header):
	def __init__(self, arg):
		super(UDPHeader, self).__init__()
		self.arg = arg
		
class IPHeader(Header):
	def __init__(self, size, orig, dest, prot):
		super(IPHeader, self).__init__()
		self.size = size
		self.dest = dest
		self.orig = orig
		self.prot = prot

class Agent(object):
	def __init__(self, name):
		self.owner = ""
		self._name = name
		pass	

	def SetOwner(self, o):
		print self._name, "associado a", o
		self.owner = o

class Sniffer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		print "sniffer criado ", name
		self.type = "sniffer"

	def SetLogFile(self, path):
		print name, "log salvo em", path
		self.logPath = path

class HttpClient(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		print "Http Server criado ", name
		self.type = "httpc"

	def isIp(self, dest):
		dl = dest.split(".")
		if len(dl) == 4:
			for e in dl:
				if not e.isdigit():
					return False
			return True
		return False

	def Get(self, dest, ent):
		if self.isIp(dest):
			print "To mandando o get"
		else:
			o = ent[self.owner]
			hip = IPHeader(40, o.me, o.dns, 17)
			udpp = Packet()
			o.SendPackets(40, hip)
			

class HttpServer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		print "Http Client criado ", name
		self.type = "https"


class DNSServer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		print "DNS Server criado ", name
		self.type = "dnss"
		
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

	def SetDestination(self, d, p, destEnt):
		self.destinationName = d
		self.destinationPort = p #if its not a router, it should be -1
		self.destination = destEnt

	def ExchangePackets(self): #restringir a velocidade
		targetEntity = simulatorSingleton.entities[self.destinationName]
		for p in self.packets:
			targetEntity.ReceivePacket(p)

# May also be refered to as a device. Its an abstraction
# for both Host and Router
class Entity(object): 
	def __init__(self, name):
		self._type = type(self)
		Entity.host = type(Host("")) #save the type of a host for future consultation
		Entity.router = type(Router("", -1))#save the type of a router for future consultation
		self.agents = {}
		self.sendBuffer = []
		self.recBuffer = []
		self._name = name

	def Loop():
		pass

	def GetType(self):
		return self._type

	def ReceivePacket(self, packet):
		pass

	def AttachAgent(self, agName, ag):
		self.agents[agName]  = ag
		ag.SetOwner(self._name)

	def GetRecLink(self, entities, sendLink):
		self.dest = entities[sendLink.destinationName]
		if self.dest.GetType() == Entity.router:
			self.port = sendLink.destinationPort
			return self.dest.links[self.port]
		return self.dest.links[0]

class Host(Entity):
	def __init__(self, name):
		if(name == ""):
			return
		Entity.__init__(self, name)
		print "Host criado ", name
		self.links = []

	def Loop(self, entities):
		print "executando host ", self._name
		self.cont = False
		self.cont  = self.cont or len(self.links[0].packets) > 0

		self.recLink = self.GetRecLink(entities, self.links[0])

		if len(self.recLink.packets) > 0:
			self.ReceivePacket(self.recLink.packets[0], self.recLink)

		return self.cont

	def SetLink(self, d, s, dest, destp, destEnt):
		newLink = Link()
		newLink.SetSpeed(s)
		newLink.SetDelay(d)
		newLink.SetDestination(dest, destp, destEnt)
		self.links.append(newLink)

	def SetIps(self, host, router, dns):
		self.me = host
		self.router = router
		self.dns = dns[:-1]
		print "\n", self._name, ":"
		print "ip", self.me
		print "router", router
		print "DNS:", dns[:-1], "\n"

	def GetLink(self):
		return self.links

	def PrintLinks(self):
		if not self.links.destinationPort == -1:
			print self._name, "-->", str(self.links.destinationName)+"."+str(self.links.destinationPort), str(self.links.speed)+"ms", str(self.links.delay)+ "Mbps"
		else:
			print self._name, "-->", self.links.destinationName, str(self.links.speed)+"ms", str(self.links.delay), "Mbps"

	def SendPackets(self, dataSize, header):
		# Checar se eh um ip ou um endereco
		# if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
		numPackets = dataSize / packetSize

		numPackets += 1

		print "SENDING PACKET from", self._name, "to", header.dest
		# now hosts have support for more then one link, 
		# but they should not have more then one
		for li in  self.links:
			if not li.destinationName == self._name:
				self.l = li

		for i in range(0, numPackets):
			p = Packet()
			p.SetHeader(header)
			self.l.packets.append(p)

	def ReceivePacket(self, packet, recLink):
		if packet.header.dest == self.me:
			print "Packet chegou no lugar certo"
		else:
			print self._name, "transmitting packet"
			self.links[0].packets.append(packet)
		del recLink.packets[0]

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
		print "adding route", orig, dest
		self.routes[orig] = dest

	def SetLink(self, d, s, dest, destp, port, destEnt):
		if port > self.interfacesCount:
			print "porta inexistente"
			return
 
		self.links[port].SetSpeed(s)
		self.links[port].SetDelay(d)
		self.links[port].SetDestination(dest, destp, destEnt)

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

	def Loop(self, entities):
		print "executando router ", self._name
		self.ret = False
		for l in self.links:
			self.recLink = self.GetRecLink(entities, l)
			if len(self.recLink.packets) > 0:
				self.ReceivePacket(self.recLink.packets[0], self.recLink)
				self.ret = True
		return self.ret

	def isIp(self, dest):
		dl = dest.split(".")
		if len(dl) == 4:
			for e in dl:
				if not e.isdigit():
					return False
			return True
		return False

	#check if dev a and b are in the same network
	def SameSubNet(self, a, b):
		aFields = a.split(".")
		bFields = b.split(".")
		self.ok = True
		self.ok &= aFields[0] == bFields[0]
		self.ok &= aFields[1] == bFields[1]
		self.ok &= aFields[2] == bFields[2]
		return self.ok

	#checks if x could be indentifyed by ip address a
	def IsTheSame(self, x, a):

		if x.GetType == Entity.host:
			if x.me == a:
				return True
		else:
			for i in x.ips:
				if i[0] == a:
					return True
		
		return False

	def ReceivePacket(self, packet, recLink):
		del recLink.packets[0]
		print self._name, "transmitting packet to", packet.header.dest		
		for k in self.routes.keys():
			if self.SameSubNet(packet.header.dest, k):
				if not self.isIp(self.routes[k]):
					self.links[int(self.routes[k])].packets.append(packet)
				else:
					for l in self.links:
						if self.IsTheSame(l.destination, self.routes[k]):
							l.packets.append(packet)
