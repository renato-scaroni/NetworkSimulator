from operator import itemgetter
import sys

simulatorSingleton = None
packetSize = 1024 * 8 * 500 #500 kbytes
UDPID = 0
PACKID = 0
DNSTABLE = {}
DEBUG = False
CLOCK = 0
TIMESTEP =  0.000001
def debugPrint(s1, s2="", s3="", s4="", s5=""):
	if DEBUG:
		print s1, s2, s3, s4

class EP3Simulator(object):
	def __init__(self, entities, agents):
		global simulatorSingleton
		self.entities = entities
		self.agents = agents
		self.commands = []
		simulatorSingleton = self

	def SetCommands(self, c): # a command is a tuple (time, commandString)
		self.commands = c

	def ParseAndExecuteCommand(self, cmd):
		debugPrint ("Comando: " + cmd)
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
			debugPrint ("commands to execute :")
			for c in self.commands:
				debugPrint (c)
			self.time = float(self.commands[0][0])
		else:
			debugPrint ("Nao existem comandos a serem executados")
			return

		for k in self.entities.keys():
			self.entities[k].PrintLinks()
		global CLOCK
		CLOCK = 0
		global PACKID
		PACKID = 0

		opf = open(outputFile, "w+")

		for k in self.agents.keys():
			if self.agents[k].type == "sniffer":
				self.agents[k].SetOutputFile(opf)

		keepSimulating = True
		while keepSimulating or len(self.commands) > 0:
			for c in self.commands:
				if float(c[0]) < float(CLOCK):
					if not self.ParseAndExecuteCommand(c[1]): self.commands = []
					else: self.commands = [s for s in self.commands if s != c]

			keepSimulating = False
			for k in self.entities.keys():
				keepSimulating = self.entities[k].Loop(self.entities) or keepSimulating
				# self.entities[k].PrintLinks()
			CLOCK += TIMESTEP

class Packet(object):
	def __init__(self):
		self.data = None
		self.header = None
		self.proc = 0
		global PACKID
		self.id = PACKID
		PACKID += 1

	def SetHeader(self, h):
		self.header = h

	def SetProtHeader(self, h):
		self.protHeader = h

	def SetData(self, data):
		self.data = data

	def ProcessPacket(self):
		self.proc += TIMESTEP*100000

class Header(object):
	def __init__(self):
		super(Header, self).__init__()

	def SetSize(self, s):
		self.size = s #int

class UDPHeader(Header):
	# orig e dest are the port used by the service
	def __init__(self, orig, dest):
		super(UDPHeader, self).__init__()
		self.dest = dest #string
		self.orig = orig #string
		global UDPID
		self.id = UDPID
		UDPID += 1

class IPHeader(Header):
	def __init__(self, orig, dest, prot, ttl):
		super(IPHeader, self).__init__()
		self.dest = dest #string
		self.orig = orig #string
		self.prot = prot #int
		self.ttl = ttl

class Agent(object):
	def __init__(self, name):
		self.owner = None
		self._name = name
		pass	

	def SetOwner(self, o):
		debugPrint (self._name, "associado a", o._name)
		self.owner = o

class Sniffer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		debugPrint ("sniffer criado ", name)
		self._name = name
		self.type = "sniffer"
		self.logFile = None

	def SetOutputFile(self, opf):
		self.opf = opf

	def SetLogFile(self, path):
		debugPrint (self._name, "log salvo em", path)
		self.logPath = path

		self.logFile = open(self.logPath, 'w+')

	def Log(self, p):
		debugPrint ("to fazenu logui")

		if self.logFile == None:
			debugPrint("criano logui")

		toPrint =  "Pacote: " + str(p.id) + "\n"
		toPrint +=  "Tempo: " + str(CLOCK) + "\n"
		toPrint += "Sniffer: " + self._name + "\n"
		toPrint += "\n"
		toPrint += "IP: " + "\n"
		toPrint += "Endereco de origem: " + p.header.orig + "\n"
		toPrint += "Endereco de destino: " + p.header.dest + "\n"
		toPrint += "Protocolo da camada acima: " + str(p.header.prot) + "\n"
		toPrint += "Tamanho na camada superior: " + str(p.header.size) + "\n"
		toPrint += "TTL: " + str(p.header.ttl) + "\n"
		toPrint += "\n"
		toPrint += "UDP: " + "\n"
		toPrint += "Porta de origem: " + str(p.protHeader.orig) + "\n"
		toPrint += "Porta de destino: " + str(p.protHeader.dest) + "\n"
		toPrint += "Tamanho na camada superior: " + str(p.protHeader.size) + "\n"
		toPrint += "\n"
		if p.data.ip == -1:	
			toPrint += "Mensagem DNS: resolvendo nome para " + p.data.msg + "\n"
		else:
			toPrint += "Mensagem DNS: "+ p.data.msg + "=" + p.data.ip + "\n"
		toPrint += "-------------------------------------------------------------\n"

		self.logFile.write(toPrint)
		print toPrint

class DNSMessage:
	def __init__(self, t, msg, ip=-1):
		self.type = t
		self.msg = msg
		self.ip = ip

class HttpClient(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		debugPrint ("Http Server criado ", name)
		self.type = "httpc"
		self.cmdQueue = []

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
			debugPrint ("To mandando o get para", dest)
		else:
			o = self.owner
			hip = IPHeader(o.me, o.dns, 17, 86400) # 6 se for TCP
			hudp = UDPHeader(53, 53)
			data = DNSMessage("Q", dest)
			o.SendPackets(hip, hudp, data)
			self.cmdQueue.append("get")
			o.waitingAgents.append((dest, self))

	def ResumeCmd(self, dnsMsg):
		if len(self.cmdQueue) and self.cmdQueue[0] == "get":
			debugPrint ("To mandando o get para", dnsMsg.ip)

class HttpServer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		debugPrint ("Http Client criado ", name)
		self.type = "https"

class DNSServer(Agent):
	def __init__(self, name):
		Agent.__init__(self, name)
		debugPrint ("DNS Server criado ", name)
		self.type = "dnss"

	def HandleMessage(self, p):		
		name = p.data.msg
		if name in DNSTABLE.keys() and p.data.type == "Q":
			debugPrint ("traduzindo", name, "para", DNSTABLE[name])
			o = self.owner
			hip = IPHeader(o.me, p.header.orig, 17, 86400) # 6 se for TCP
			hudp = UDPHeader(53, 53)
			data = DNSMessage("R", name, DNSTABLE[name])
			o.SendPackets(hip, hudp, data)
		elif p.data.type == "R":
			debugPrint (self.owner._name, "recebeu uma response de DNS")
		
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
			debugPrint ("sniffer no link para", self.destinationName)
		else:
			debugPrint ("sniffer no link para", str(self.destinationName)+ "." +str(self.destinationPort))
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

	def RunSniffer(self, p):
		if self.sniffer:
			self.sniffer.Log(p)

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
		ag.SetOwner(self)

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
		debugPrint ("Host criado ", name)
		self.links = []
		self.waitingAgents = []

	def Loop(self, entities):
		debugPrint ("executando host ", self._name)
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
		debugPrint ("\n", self._name, ":")
		debugPrint ("ip", self.me)
		debugPrint ("router", router)
		debugPrint ("DNS:", dns[:-1], "\n")

	def GetLink(self):
		return self.links

	def PrintLinks(self):
		if not self.links[0].destinationPort == -1:
			debugPrint (self._name, "-->", str(self.links[0].destinationName)+"."+str(self.links[0].destinationPort), str(self.links[0].speed)+"ms", str(self.links[0].delay)+ "Mbps")
		else:
			debugPrint (self._name, "-->", self.links[0].destinationName, str(self.links[0].speed)+"ms", str(self.links[0].delay), "Mbps")

	def SendPackets(self, hip, hudp, data):
		# Checar se eh um ip ou um endereco
		# if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
		hudp.SetSize (sys.getsizeof(hudp) + sys.getsizeof(data))
		dataSize = sys.getsizeof(hip) +  hudp.size
		hip.SetSize (dataSize)
		numPackets = dataSize / packetSize

		numPackets += 1

		debugPrint ("SENDING PACKET from", self._name, "to", hip.dest)
		# now hosts have support for more then one link, 
		# but they should not have more then one
		for li in  self.links:
			if not li.destinationName == self._name:
				self.l = li

		for i in range(0, numPackets):
			p = Packet()
			p.SetHeader(hip)
			p.SetProtHeader(hudp)
			p.SetData(data)
			self.l.packets.append(p)
			self.l.RunSniffer(p)

	def ReceivePacket(self, packet, recLink):
		if packet.header.dest == self.me:
			if packet.header.prot == 17 and packet.protHeader.dest == 53:
				for a in self.agents.keys():
					if "dns" in a:
						self.agents[a].HandleMessage(packet)
				for a in self.waitingAgents:
					if a[0] == packet.data.msg:
						a[1].ResumeCmd(packet.data)

		else:
			debugPrint (self._name, "transmitting packet")
			self.links[0].packets.append(packet)
			self.links[0].RunSniffer(packet)
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
		
		debugPrint ("Router criado ", name)
		
		self._name = name

		#this list will keep tuples with the ports and ips 
		#that will indentify this router
		self.ips = []

		#this dict will keep the routes table
		self.routes = {}

		#time consumed by the router to process 1 packet
		self.procTime = 0

	def SetRoutes(self, orig, dest):
		debugPrint ("adding route", orig, dest)
		self.routes[orig] = dest

	def SetLink(self, d, s, dest, destp, port, destEnt):
		if port > self.interfacesCount:
			debugPrint ("porta inexistente")
			return
 
		self.links[port].SetSpeed(s)
		self.links[port].SetDelay(d)
		self.links[port].SetDestination(dest, destp, destEnt)

	def SetIps(self, ip, port):
		self.ips.append((ip, port))
		debugPrint ("orig", ip)
		debugPrint ("dest", port, "\n")

	def SetProcTime(self, p):
		debugPrint ("Tempo de processamento de pacotes", p)
		self.procTime = p

	def SetMaxQueueForPort(self, port, l):		
		self.maxPacketQueue[port] = l
		debugPrint ("porta", port)
		debugPrint ("limite", l, "\n")

	def GetLink(self, port):
		return self.links[int(port)]

	def PrintLinks(self):
		for i in range(self.interfacesCount):
			l = self.links[i]
			if not l.destinationPort == -1:
				debugPrint (self._name+"."+str(i), "-->", str(l.destinationName) + "."+ str(l.destinationPort), str(l.speed)+"ms", str(l.delay)+ "Mbps")
			else:
				debugPrint (self._name+"."+str(i), "-->", l.destinationName, str(l.speed)+"ms", str(l.delay)+ "Mbps")

	def Loop(self, entities):
		debugPrint ("executando router ", self._name)
		self.ret = False
		for l in self.links:
			self.recLink = self.GetRecLink(entities, l)
			if len(self.recLink.packets) > 0:
				if self.recLink.packets[0].proc < int(self.procTime):
					self.recLink.packets[0].ProcessPacket()
				else:
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
		if x.GetType() == Entity.host:
			if x.me == a:
				return True
		else:
			for i in x.ips:
				if i[0] == a:
					return True
		
		return False

	def ReceivePacket(self, packet, recLink):
		del recLink.packets[0]
		debugPrint (self._name, "trying to transmit packet to", packet.header.dest		)
		for k in self.routes.keys():
			if self.SameSubNet(packet.header.dest, k):
				if not self.isIp(self.routes[k]):
					debugPrint (self._name, "actually transmitting packet to", packet.header.dest		)
					self.links[int(self.routes[k])].packets.append(packet)
					self.links[int(self.routes[k])].RunSniffer(packet)
				else:
					for l in self.links:
						if self.IsTheSame(l.destination, self.routes[k]):
							l.packets.append(packet)
							l.RunSniffer(packet)