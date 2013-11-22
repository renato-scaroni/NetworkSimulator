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
			else
				agents[name] = CreateAgent



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