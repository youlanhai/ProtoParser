#-*- coding: utf-8 -*-
import os

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


class EnumDescriptor(object):
	def __init__(self, name, parent = None):
		self.name = name
		self.parent = parent
		self.type = "enum"
		self.fields = {}

	def addField(self, key, value):
		self.fields[key] = value


class IType(object):
	def __init__(self, name, type):
		super(IType, self).__init__()
		self.name = name
		self.type = type
		self.codes = []
		self.types = {}
		self.options = {}

	def addOption(self, name, value):
		self.options[name] = value

	def addType(self, tp):
		if tp in self.types:
			raise TypeError, "type '%s' has been exist" % tp.name
		self.types[tp.name] = tp
		self.codes.append(tp)

	def isTypeExist(self, name):
		return name in self.types

	def getType(self, name):
		return self.types.get(name)

	def findType(self, name):
		return self.getType(name)


class ClassDescriptor(IType):
	''' 消息类
	'''
	def __init__(self, name, parent):
		super(ClassDescriptor, self).__init__(name, "message")
		self.parent = parent
		self.members = []
		self.attributes = []

	def addMember(self, varOrder, varQualifier, varName, varType, varTemplateArgs):
		member = Member(varOrder, varQualifier, varName, varType, varTemplateArgs)
		self.members.append(member)

	def setAttributes(self, attributes):
		self.attributes = attributes

	def findType(self, name):
		try:
			return self.types[name]
		except:
			return self.parent.findType(name)


class FileDescriptor(IType):
	''' 协议文件
	'''
	def __init__(self, fileName):
		super(FileDescriptor, self).__init__(fileName, "file")
		self.fileName = fileName
		self.includes = []
		self.packageName = None
		self.syntax = "proto2";

	def addInclude(self, fd):
		if fd.isFDExist(self): return False #循环包含

		self.includes.append(fd)
		return True

	def isFDExist(self, fd):
		if fd == self or fd.fileName == self.fileName: return True
		for inc in self.includes:
			if inc.isFDExist(fd): return True
		return False

	def findType(self, name):
		try:
			return self.types[name]
		except:
			pass

		for fd in self.includes:
			code = fd.findType(name)
			if code:
				return code

		return None

	def setPackageName(self, name):
		self.packageName = name

	def setSyntax(self, syntax):
		self.syntax = syntax


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
