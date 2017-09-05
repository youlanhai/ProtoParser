# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template
from Generator import Generator

class ListGenerator(Generator):
	''' 消息文件列表生成器。用于调试目的
	'''

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
				mode = attr["mode"]
				cmd = attr["cmd"]
				method = attr["method"]
				ret.append((cmd, mode, method, protoName))

		return ret

	def writeMessageList(self, messages):
		namespace = {"messages" : messages}
		
		fmt = self.template.TEMPLATE
		tpl = Template(fmt, searchList = [namespace, self])
		self.stream.write(str(tpl))

