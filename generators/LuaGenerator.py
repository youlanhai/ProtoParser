# -*- coding: utf-8 -*-
import os
from generator import Generator
from Cheetah.Template import Template

# args:  fields, method, moduleName, className, send, cmd
TPL_EXPAND_METHOD = """
#set argText = "network"
#if len($fields) > 0
#set argText = $argText + ", " + ", ".join($fields)
#end if
local function ${method}($argText)
	local proto = $moduleName.${className}()
#for field in $fields
	proto.$field = $field
#end for
	network:${send}($cmd, proto)
end
"""

TPL_COLLAPSED_METHOD = """
local function ${method}(network, proto)
	network:${send}($cmd, proto)
end
"""

# args: functions
TPL_RETURN = """
return {
#for fun in $functions
	$fun,
#end for
}
"""


class LuaGenerator(Generator):

	def __init__(self, mode = "up"):
		super(LuaGenerator, self).__init__()
		self.mode = mode

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

		for clsDesc in fileDesc.codes:
			self.writeClassCodes(indent, clsDesc)

	def writeFileHeader(self):
		self.writeLine(0, "-- this file is auto generate by ProtoParser tool.")
		self.writeLine(0, "-- from ", self.inputFile)

	def writeClassCodes(self, indent, clsDesc):
		for attr in clsDesc.attributes:
			if attr["mode"] != self.mode: continue

			self.writeMethod(indent, attr, clsDesc)
			self.writeNewLine()

			self.functions.append(attr["method"])

	def writeMethod(self, indent, attr, clsDesc):
		namespace = {
			"fields" : [member.name for member in clsDesc.members],
			"moduleName" : self.moduleName,
			"className" : clsDesc.name,
			"send" 		: attr.get("send", "send"),
			"cmd" 		: attr["cmd"],
			"method" 	: attr["method"],
		}

		text = TPL_EXPAND_METHOD if attr.get("expand", True) else TPL_COLLAPSED_METHOD
		tpl = Template(text, searchList = [namespace])
		self.stream.write(str(tpl))

	def writeReturn(self, indent, functions):
		tpl = Template(TPL_RETURN, searchList = [{"functions" : functions}])
		self.stream.write(str(tpl))
