#!/usr/bin/env python

import sys
import os
from classes import *

def CreateAgent(name, param):
	print "criando agente ", name

def CreateDevice(name, param):
	if "$simulator host" in param:
		return Host(name)
	elif "$simulator router" in param:
		numberOfInterfaces = int(param.split(" ")[3].split("]")[0])
		return Router(name, numberOfInterfaces)

def GetNumFromString(s):
	i = 0
	while not s[:-i].isdigit():
		i += 1
	return int(s[:-i])

def CreateLink(data, entities):
	origDevice = data[2][1:].split(".")[0]
	if len(data[2][1:].split(".")) >1:
		origPort = data[2][1:].split(".")[1]
	else:
		origPort = -1
	destDevice = data[3][1:].split(".")
	if len(data[3][1:].split(".")) >1:
		destPort = data[3][1:].split(".")[1]
	else:
		destPort = -1

	if entities[origDevice].GetType() == Entity.host:
		entities[origDevice].SetLink(GetNumFromString(data[4]), GetNumFromString(data[5]), destDevice[0], int(destPort))
	else:
		entities[origDevice].SetLink(GetNumFromString(data[4]), GetNumFromString(data[5]), destDevice[0], int(destPort), int(origPort))


	if entities[destDevice[0]].GetType() == Entity.host:
		entities[destDevice[0]].SetLink(GetNumFromString(data[4]), GetNumFromString(data[5]), (origDevice), int(origPort))
	else:
		entities[destDevice[0]].SetLink(GetNumFromString(data[4]), GetNumFromString(data[5]), (origDevice), int(origPort), int(destPort))

def CutLineEnding (s):
	if s[-1] == '\n':
		return s[:-1]
	return s

def ConfigureHost(h, data):
	h.SetIps(data[2], data[3], data[4])

def ConfigureRouterRoutes(r, data):
	i = 3
	print "config de rota para", data[1][1:]
	while i < len(data) - 1: 
		r.SetIps(data[i], CutLineEnding(data[i+1]))
		i = i + 2

def ConfigureRouterIps(r, data):
	i = 2
	print "\n", data[1][1:], ":"
	while i < len(data) - 1: 
		r.SetIps(CutLineEnding(data[i+1]), data[i])
		i = i + 2

def ConfigureRouterPerformance(r, data):
	print "config de perforance para", data[1][1:]
	r.SetProcTime(data[3][:-2])
	i = 4
	while i < len(data) - 1: 
		r.SetMaxQueueForPort(int(data[i]), CutLineEnding(data[i+1]))
		i = i + 2

def AttachAgent(agName, ent, agents):
	ent.AttachAgent(agName, agents[agName])

def AttachSniffer(ag, ent, data):
	#get the edges in a link
	d1 = data[3][1:].split(".") #device 1
	d2 = data[4][1:].split(".") #device 2

	#get links (both ways)
	if len(d1) > 1:
		l1 = ent[d1[0]].GetLink(d1[1])
	else:
		l1 = ent[d1[0]].GetLink()

	if len(d2) > 1:
		l2 = ent[d2[0]].GetLink(d2[1])
	else:
		l2 = ent[d2[0]].GetLink()

	l1.SetSniffer(ag[data[2][1:]])
	l2.SetSniffer(ag[data[2][1:]])

def readInput(inputFilename, outputFilename):
	entities = {}
	agents = {}
	f = open(inputFilename, "rb")
	for line in f:
		data = line.split(" ")
	
		if data[0] == "set":   #hora de criar um objeto
			name = data[1]
			param = ""
			for i in range(2, len(data)): param += " " + data[i]
			if "$simulator host" in param or "$simulator router" in param:
				entities[name] = CreateDevice(name, param)
			else:
				agents[name] = CreateAgent(name, param)
	
		if data[0] == "$simulator": #configure Host or Router
			if data[1] == "duplex-link":
				CreateLink(data, entities)
			if data[1][1:] in entities.keys():
				if entities[data[1][1:]].GetType() == Entity.host:
					ConfigureHost(entities[data[1][1:]], data)
				elif entities[data[1][1:]].GetType() == Entity.router:
					if data[2] == "performance":
						ConfigureRouterPerformance(entities[data[1][1:]], data)
					elif data[2] == "route":
						ConfigureRouterRoutes(entities[data[1][1:]], data)
					else:
						ConfigureRouterIps(entities[data[1][1:]], data)

			if data[1] == "attach-agent": # Associate Agent with Host or Router
				if data[2][1:].startswith("sniffer"):
					AttachSniffer(agents, entities, data)
				else:
					AttachAgent(data[2][1:], entities[CutLineEnding(data[3][1:])], agents)

	f.close()
	simulator = EP3Simulator(entities)
	simulator.simulate(outputFilename)


def main():
	if len(sys.argv) < 3 or len(sys.argv) > 3:
		print "Uso: ./main.py <entrada> <saida>"
		return
	readInput(sys.argv[1], sys.argv[2])


if  __name__ =='__main__':
    main()