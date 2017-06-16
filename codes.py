#-*- coding: utf-8 -*-

NUMBER_TYPES = set(("int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float", "double", ))

class Member(object):
	def __init__(self, index, qualifier, name, type, template):
		super(Member, self).__init__()
		self.index = index
		self.camelName = name
		self.name = name.lower()
		self.type = type
		self.template = template
		self.qualifier = qualifier

		self.isNumber = type in NUMBER_TYPES
		self.isVector = qualifier == "repeated"
		self.isMap = type.startswith("map")
		self.isContainer = self.isVector or self.isMap


class ClassDescriptor(object):
	def __init__(self, name, type):
		super(ClassDescriptor, self).__init__()
		self.name = name
		self.type = type
		self.members = []
		self.attributes = []

	def addMember(self, varOrder, varQualifier, varName, varType, varTemplateArgs):
		member = Member(varOrder, varQualifier, varName, varType, varTemplateArgs)
		self.members.append(member)

	def setAttributes(self, attributes):
		self.attributes = attributes


class FileDescriptor(object):
	def __init__(self, fileName):
		super(FileDescriptor, self).__init__()
		self.fileName = fileName
		self.codes = []
		self.types = set()
		self.includes = []

	def addCode(self, cls):
		self.codes.append(cls)
		self.types.add(cls.name)

	def addInclude(self, fd):
		if fd.isFDExist(self): return False #循环包含

		self.includes.append(fd)
		return True

	def isFDExist(self, fd):
		if fd == self or fd.fileName == self.fileName: return True
		for inc in self.includes:
			if inc.isFDExist(fd): return True
		return False

	def isTypeExist(self, tp):
		if tp in self.types: return True

		for fd in self.includes:
			if fd.isTypeExist(tp): return True

		return False

class Module(object):
	def __init__(self):
		super(Module, self).__init__()
		self.files = {}
		self.searchPath = []

	def isFileParsed(self, fileName):
		return fileName in self.files

	def newFileDescriptor(self, fileName):
		assert(fileName not in self.files)

		fd = FileDescriptor(fileName)
		self.files[fileName] = fd
		return fd

ATTR_KEYS = ["mode", "cmd", "method"]

class Attribute(object):
	def __init__(self):
		self.index = 0
		self.attributes = {}

	def addSingleValue(self, value):
		if self.index >= len(ATTR_KEYS):
			raise ValueError, "无效的属性 %s" % str(value)

		key = ATTR_KEYS[self.index]
		self.index += 1
		self.addPairValue(key, value)

	def addPairValue(self, key, value):
		self.attributes[key] = value
