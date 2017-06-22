# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template

from Generator import Generator
import templates


# 代码生成器基类
class NormalGenerator(Generator):

	#@param mode 	上下行模式。与message属性中的上下行模式一致。
	# 只有模式相同的属性，才会生成代码。因此，可以把mode看做是个生成代码的过滤器。
	#@param template 模板数据，描述了如何生成代码。template是templates目录下模块文件的名称。
	def __init__(self, mode = "up", template = "LuaCall"):
		super(Generator, self).__init__()
		self.stream = None
		self.mode = mode
		self.template = getattr(templates, template)

	def generate(self, inputFile, outputFile, fileDesc):
		self.inputFile = inputFile
		self.moduleName = os.path.splitext(os.path.basename(inputFile))[0]
		self.fileDesc = fileDesc

		self.functions = []

		with open(outputFile, "wb") as f:
			self.stream = f

			self.writeFileCodes(fileDesc)
			self.writeReturn(self.functions)

		return

	def writeFileCodes(self, fileDesc):
		self.writeFileHeader()
		self.writeNewLine()

		for clsDesc in fileDesc.codes:
			self.writeClassCodes(clsDesc)

	def writeFileHeader(self):
		fmt = self.template.HEADER
		tpl = Template(fmt, searchList = [self])
		self.stream.write(str(tpl))

	def writeClassCodes(self, clsDesc):
		for attr in clsDesc.attributes:
			if attr["mode"] != self.mode: continue

			self.writeCallMethod(attr, clsDesc)
			self.writeNewLine()

			self.functions.append((attr["cmd"], attr["method"]))

	def genMethodNamespace(self, attr, clsDesc):
		return {
			"fields" : [member.name for member in clsDesc.members],
			"moduleName" : self.moduleName,
			"className" : clsDesc.name,
			"send" 		: attr.get("send", "sendProto"),
			"cmd" 		: attr["cmd"],
			"method" 	: attr["method"],
		}

	def writeCallMethod(self, attr, clsDesc):
		namespace = self.genMethodNamespace(attr, clsDesc)

		fmt = None
		if attr.get("expand", True):
			fmt = self.template.EXPAND_METHOD
		else:
			fmt = self.template.COLLAPSED_METHOD

		tpl = Template(fmt, searchList = [namespace, self])
		self.stream.write(str(tpl))


	def writeReturn(self, functions):
		namespace = {"functions" : functions}
		fmt = self.template.RETURN
		tpl = Template(fmt, searchList = [namespace, self])
		self.stream.write(str(tpl))
