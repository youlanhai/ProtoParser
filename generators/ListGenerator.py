# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template
from Generator import Generator
import templates

class ListGenerator(Generator):

	def __init__(self, template = "LuaList"):
		super(ListGenerator, self).__init__()
		self.template = getattr(templates, template)

	def generate(self, inputFile, outputFile, fileDesc):
		self.inputFile = inputFile
		self.moduleName = os.path.splitext(os.path.basename(inputFile))[0]
		self.fileDesc = fileDesc

		with open(outputFile, "wb") as f:
			self.stream = f

			self.writeMessageList(self.collectMessages(fileDesc))

	def collectMessages(self, fileDesc):
		ret = []

		for clsDesc in fileDesc.codes:
			protoName = "%s.%s" % (self.moduleName, clsDesc.name)
			for attr in clsDesc.attributes:
				cmd = attr["cmd"]
				method = attr["method"]
				ret.append((cmd, method, protoName))

		return ret

	def writeMessageList(self, messages):
		namespace = {"messages" : messages}
		
		fmt = self.template.LIST
		tpl = Template(fmt, searchList = [namespace, self])
		self.stream.write(str(tpl))

