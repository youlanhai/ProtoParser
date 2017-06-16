# -*- coding: utf-8 -*-
import os
from generator import Generator

class ListGenerator(Generator):

	def generate(self, inputFile, outputFile, fileDesc):
		self.inputFile = inputFile
		self.moduleName = os.path.splitext(os.path.basename(inputFile))[0]
		self.fileDesc = fileDesc

		with open(outputFile + ".json", "wb") as f:
			self.stream = f

			self.writeMessageList(0, self.collectMessages(fileDesc))

	def collectMessages(self, fileDesc):
		ret = []

		for clsDesc in fileDesc.codes:
			protoName = "%s.%s" % (self.moduleName, clsDesc.name)
			for attr in clsDesc.attributes:
				cmd = attr["cmd"]
				method = attr["method"]
				ret.append((cmd, method, protoName))

		return ret

	def writeMessageList(self, indent, messages):
		self.writeLine(indent, "[")
		indent += 1
		for i, message in enumerate(messages):
			text = """[%d, "%s", "%s"]""" % message
			if i + 1 == len(messages):
				self.writeLine(indent, text)
			else:
				self.writeLine(indent, text, ",")
		indent -= 1
		self.writeLine(indent, "]")

