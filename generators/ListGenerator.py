# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template
from .Generator import Generator

class ListGenerator(Generator):
	''' 消息文件列表生成器。用于调试目的
	'''

	def generate(self, inputFile, outputFile, module):
		self.inputFile = inputFile
		self.moduleName = os.path.splitext(os.path.basename(inputFile))[0]

		ret = []
		with open(outputFile, "w", newline="\n") as f:
			self.stream = f

			for fileDesc in module.files.values():
				self.collectMessages(ret, fileDesc)

			self.writeMessageList(ret)

	def collectMessages(self, ret, fileDesc):
		for clsDesc in fileDesc.codes:
			if clsDesc.type != "message": continue

			protoName = "%s.%s" % (self.moduleName, clsDesc.name)
			for attr in clsDesc.attributes:
				mode = attr["mode"]
				cmd = attr["cmd"]
				method = attr["method"]
				ret.append((cmd, mode, method, protoName))
		return

	def writeMessageList(self, messages):
		split = {"up" : [], "dn" : []}
		for msg in messages:
			split[msg[1]].append(msg)

		namespace = {
			"messages" : messages,
			"up_messages" : split["up"],
			"dn_messages" : split["dn"],
		}
		
		fmt = self.template.TEMPLATE
		tpl = Template(fmt, searchList = [namespace, self, self.template])
		self.stream.write(str(tpl))

