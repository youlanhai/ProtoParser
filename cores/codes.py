#-*- coding: utf-8 -*-
import os

NUMBER_TYPES = set((
	"int8",
	"uint8",
	"int16",
	"uint16",
	"int32",
	"uint32",
	"int64",
	"uint64",
	"float",
	"double",
))

class Member(object):
	''' 消息的成员变量
	'''
	def __init__(self, index, qualifier, name, type, template):
		super(Member, self).__init__()
		self.index = index
		self.name = name
		self.type = type
		self.template = template
		self.qualifier = qualifier

		self.isNumber = type in NUMBER_TYPES
		self.isVector = qualifier == "repeated"
		self.isMap = type.startswith("map")
		self.isContainer = self.isVector or self.isMap


class ClassDescriptor(object):
	''' 消息类
	'''
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
	''' 协议文件
	'''
	def __init__(self, fileName):
		super(FileDescriptor, self).__init__()
		self.fileName = fileName
		self.codes = []
		self.types = set()
		self.includes = []
		self.packageName = None

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
		return tp in self.types

	def findType(self, name):
		if name in self.types:
			for code in self.codes:
				if name == code.name:
					return code
		for fd in self.includes:
			code = fd.findType(name)
			if code:
				return code

		return None

	def setPackageName(self, name):
		self.packageName = name

class Module(object):
	''' 工程模块
	'''
	def __init__(self, attrIDCounter = 0):
		super(Module, self).__init__()
		self.files = {}
		self.searchPath = []
		self.attrIDCounter = attrIDCounter

	def isFileParsed(self, fileName):
		return fileName in self.files

	def newFileDescriptor(self, fileName):
		assert(fileName not in self.files)

		fd = FileDescriptor(fileName)
		self.files[fileName] = fd
		return fd

	def allocateAttrID(self):
		''' 分配属性id
		'''
		self.attrIDCounter += 1
		return self.attrIDCounter

	def findFileFullPath(self, fname):
		for path in self.searchPath:
			fullPath = os.path.join(path, fname)
			if os.path.isfile(fullPath):
				return fullPath

		return None

ATTR_KEYS = ["mode", "cmd", "method"]

class Attribute(object):
	'''消息属性。'//@'开头的行，格式::

		[mode, cmd, method, key=value, ...]

	'''
	def __init__(self, id = 0):
		self.id = id
		self.index = 0
		self.attributes = {}

	def addSingleValue(self, value):
		''' 添加值属性。会根据索引位置，自动转换成键-值对格式
		'''
		if self.index >= len(ATTR_KEYS):
			raise ValueError, "无效的属性 %s" % str(value)

		# 如果未指定协议号，则自动生成
		if self.index == 1 and isinstance(value, str):
			self.addPairValue("cmd", self.id)
			self.index += 1

		key = ATTR_KEYS[self.index]
		self.index += 1
		self.addPairValue(key, value)

	def addPairValue(self, key, value):
		''' 添加键-值对属性
		'''
		self.attributes[key] = value
