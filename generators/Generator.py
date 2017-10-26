# -*- coding: utf-8 -*-
import templates

INDENT_CHAR = "    "
NEW_LINE = "\n"

# 代码生成器基类
class Generator(object):

	def __init__(self, generatorInfo, exporter):
		super(Generator, self).__init__()
		self.generatorInfo = generatorInfo
		self.exporter = exporter
		self.stream = None
		self.template = None

		tplName = generatorInfo.get("template")
		if tplName:
			self.template = getattr(templates, tplName)

	def write(self, indent, *args):
		if indent > 0: self.stream.write(INDENT_CHAR * indent)
		for text in args: self.stream.write(text)

	def writeLine(self, indent, *args):
		if indent > 0: self.stream.write(INDENT_CHAR * indent)
		for text in args: self.stream.write(text)
		self.stream.write(NEW_LINE)

	def writeNewLine(self, n = 1):
		if n > 0: self.stream.write(NEW_LINE * n)

	# 生成代码。
	#@param inputFile 	输入文件路径
	#@param outputFile 	输出文件路径
	#@param code 		protobuf文件描述类或者是模块
	def generate(self, inputPath, outputPath, code):
		pass
