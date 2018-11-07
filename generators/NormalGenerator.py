# -*- coding: utf-8 -*-
import os
import re
from Cheetah.Template import Template

from Generator import Generator

class NormalGenerator(Generator):
	''' 通用代码生成器，针对单个输入文件，输出一个生成后的文件
	'''

	def __init__(self, generatorInfo, exporter):
		''' 生成器信息需要包含以下参数：
			mode 	上下行模式。与message属性中的上下行模式一致。只有模式相同的属性，才会生成代码。因此，可以把mode看做是个生成代码的过滤器。
			template 模板数据，描述了如何生成代码。template是templates目录下模块文件的名称。
		'''

		super(NormalGenerator, self).__init__(generatorInfo, exporter)

		self.mode = generatorInfo["mode"]

	def generate(self, inputPath, outputPath, fileDescriptor):
		self.fileDescriptor = fileDescriptor
		self.fileName = os.path.splitext(inputPath)[0]
		self.moduleName = "_".join(re.split(r"\W+", self.fileName))
		# self.packagePrefix = ""
		# if fileDescriptor.packageName:
		# 	self.packagePrefix = fileDescriptor.packageName + "."

		# 记录函数列表
		self.functions = []

		with open(outputPath, "wb") as f:
			self.stream = f

			self.writeHeader()
			self.writeNewLine()

			self.writeFileCodes(fileDescriptor.codes)

			self.writeReturn(self.functions)

		return

	def writeFileCodes(self, codes):
		self.writeFileBegin()

		for clsDesc in codes:
			if clsDesc.type == "message":
				self.writeClassCodes(clsDesc)

		self.writeFileEnd()

	def writeFileBegin(self):
		fmt = getattr(self.template, "BEGIN", None)
		if not fmt: return

		tpl = Template(fmt, searchList = [self])
		self.stream.write(str(tpl))
		self.writeNewLine()

	def writeFileEnd(self):
		fmt = getattr(self.template, "END", None)
		if not fmt: return

		tpl = Template(fmt, searchList = [self])
		self.stream.write(str(tpl))
		self.writeNewLine()

	def writeClassCodes(self, clsDesc):
		for attr in clsDesc.attributes:
			if attr["mode"] != self.mode: continue

			self.writeCallMethod(attr, clsDesc)
			self.writeNewLine()

			self.functions.append((attr["cmd"], attr["method"]))

	def genMethodNamespace(self, attr, clsDesc):
		return {
			"fileDescriptor" : self.fileDescriptor,
			"classDescriptor" : clsDesc,
			"fields" : [member.name for member in clsDesc.members],
			"moduleName" : self.moduleName,
			"className" : clsDesc.name,
			"send" 		: attr.get("send", "sendProto"),
			"cmd" 		: attr["cmd"],
			"method" 	: attr["method"],
			"comment" 	: clsDesc.getOption("comment"),
		}

	def writeCallMethod(self, attr, clsDesc):
		namespace = self.genMethodNamespace(attr, clsDesc)

		fmt = None
		if attr.get("expand", True):
			fmt = self.template.EXPAND_METHOD
		else:
			fmt = self.template.COLLAPSED_METHOD

		tpl = Template(fmt, searchList = [namespace, self, self.template])
		self.stream.write(str(tpl))


	def writeHeader(self):
		fmt = getattr(self.template, "HEADER", None)
		if not fmt: return
		
		tpl = Template(fmt, searchList = [self])
		self.stream.write(str(tpl))

	def writeReturn(self, functions):
		fmt = getattr(self.template, "RETURN", None)
		if not fmt: return

		namespace = {"functions" : functions}
		tpl = Template(fmt, searchList = [namespace, self, self.template])
		self.stream.write(str(tpl))
