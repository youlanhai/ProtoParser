# -*- coding: utf-8 -*-
import os
from generator import Generator

class LuaGenerator(Generator):

	def __init__(self):
		super(LuaGenerator, self).__init__()

	def generate(self, inputFile, outputFile, fileDesc):
		self.inputFile = inputFile
		self.moduleName = os.path.splitext(os.path.basename(inputFile))[0]
		self.fileDesc = fileDesc

		self.functions = []

		with open(outputFile + ".lua", "wb") as f:
			self.stream = f

			indent = 0

			self.writeFileCodes(indent, fileDesc)
			self.writeReturn(indent, self.functions)

	def writeFileCodes(self, indent, fileDesc):
		self.writeFileHeader()
		self.writeNewLine()

		indent = 0
		for clsDesc in fileDesc.codes:
			if len(clsDesc.attributes) == 0:
				continue

			self.writeClassCodes(indent, clsDesc)

	def writeFileHeader(self):
		self.writeLine(0, "-- this file is auto generate by ProtoParser tool.")
		self.writeLine(0, "-- from ", self.inputFile)

	def writeClassCodes(self, indent, clsDesc):
		for attr in clsDesc.attributes:
			if attr["mode"] != "up": continue

			if attr.get("expand", True):
				self.writeExpandMethod(indent, attr, clsDesc)
			else:
				self.writeCollapsedMethod(indent, attr, clsDesc)
			self.writeNewLine()

			self.functions.append(attr["method"])

	def writeExpandMethod(self, indent, attr, clsDesc):
		cmd = attr["cmd"]
		method = attr["method"]

		args = [member.name for member in clsDesc.members]

		argText = "network"
		if len(args) > 0:
			argText += ", "
			argText += ", ".join(args)

		self.writeLine(indent, "local function %s(%s)" % (method, argText))
		indent += 1

		key = "proto"
		self.writeLine(indent, "%s = %s.%s()" % (key, self.moduleName, clsDesc.name))
		for arg in args:
			self.writeLine(indent, "%s.%s = %s" % (key, arg, arg))

		self.writeNewLine()
		self.writeLine(indent, "network:send(%d, %s)" % (cmd, key))

		indent -= 1
		self.writeLine(indent, "end")

	def writeCollapsedMethod(self, indent, attr, clsDesc):
		cmd = attr["cmd"]
		method = attr["method"]

		self.writeLine(indent, "local function %s(network, proto)" % method)
		indent += 1
		self.writeLine(indent, "network:send(%d, proto)" % cmd)
		indent -= 1
		self.writeLine(indent, "end")

	def writeReturn(self, indent, functions):
		self.writeLine(indent, "return {")
		indent += 1
		for fun in functions:
			self.writeLine(indent, fun, ",")
		indent -= 1
		self.writeLine(indent, "}")
