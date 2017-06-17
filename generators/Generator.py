# -*- coding: utf-8 -*-

INDENT_CHAR = "    "
NEW_LINE = "\n"

# 代码生成器基类
class Generator(object):

	#@param mode 	上下行模式。与message属性中的上下行模式一致。
	# 只有模式相同的属性，才会生成代码。因此，可以把mode看做是个生成代码的过滤器。
	#@param template 模板数据，描述了如何生成代码。template是templates目录下模块文件的名称。
	def __init__(self, mode = "up", template = "LuaCall"):
		super(Generator, self).__init__()
		self.stream = None
		self.mode = mode
		self.template = getattr(templates, template)

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
	#@param fileDesc 	protobuf文件描述类
	def generate(self, inputFile, outputFile, fileDesc):
		pass
