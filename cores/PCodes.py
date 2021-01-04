#-*- coding: utf-8 -*-
import os
import ppconfig
import json

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

class IType(object):
	def __init__(self, name, type):
		super(IType, self).__init__()
		self.name = name
		self.type = type
		# 内嵌代码和类型
		self.codes = []
		self.types = {}
		# 类型描述信息
		self.options = {}

	@property
	def fullName(self):
		return self.name

	def addOption(self, name, value):
		self.options[name] = value

	def getOption(self, name):
		return self.options.get(name)

	def addType(self, tp):
		if tp in self.types:
			raise TypeError("type '%s' has been exist" % tp.name)
		self.types[tp.name] = tp
		self.codes.append(tp)

	def isTypeExist(self, name):
		return name in self.types

	def getType(self, name):
		return self.types.get(name)

	def findType(self, name):
		return self.getType(name)


class EnumDescriptor(IType):
	''' 枚举类
	'''
	def __init__(self, name, parent = None):
		super(EnumDescriptor, self).__init__(name, "enum")
		self.parent = parent
		self.fields = {}
	
	@property
	def fullName(self):
		if self._fullName is None:
			parentName = self.parent.fullName
			self._fullName = parentName + "." + self.name if parentName else self.name
		return self._fullName

	def addField(self, key, value):
		self.fields[key] = value

class ClassDescriptor(IType):
	''' 消息类
	'''
	def __init__(self, name, parent):
		super(ClassDescriptor, self).__init__(name, "message")
		self.parent = parent
		self.members = []
		self.attributes = []
		self._fullName = None
		self.customConfig = {}

	@property
	def fullName(self):
		if self._fullName is None:
			parentName = self.parent.fullName
			self._fullName = parentName + "." + self.name if parentName else self.name
		return self._fullName

	def addMember(self, varOrder, varQualifier, varName, varType, varTemplateArgs):
		member = Member(varOrder, varQualifier, varName, varType, varTemplateArgs)
		self.members.append(member)

	def setAttributes(self, attributes):
		# 从协议属性中提取协议号
		cmd = self.getOption(ppconfig.CMD_OPTION_NAME)
		# 未指定协议号的，自动分配协议号id
		for attr in attributes:
			if "cmd" not in attr.attributes:
				attr.updatePairValue("cmd", cmd or attr.id)

		if len(attributes) > 0:
			self.attributes = [attr.attributes for attr in attributes]
		elif cmd is not None:
			# 从配置中读取展开状态，避免修改参数后，函数声明格式发生变化
			expand = self.customConfig.get("expand")
			if expand is None:
				expand = len(self.members) <= ppconfig.MAX_EXPAND_ARGS
				self.customConfig["expand"] = expand
				
			# 自动生成属性
			self.attributes = [
				{
					"mode" : "up",
					"cmd" : cmd,
					"expand" : expand,
				},
				{
					"mode" : "dn",
					"cmd" : cmd,
					"expand" : expand,
				},
			]

		for attr in self.attributes:
			if "method" not in attr:
				mode = attr["mode"]
				attr["method"] = ppconfig.METHOD_PREFIX.get(mode, "") + self.name

	def findType(self, name):
		try:
			return self.types[name]
		except:
			return self.parent.findType(name)

	def setCustomConfig(self, config):
		self.customConfig = config


class FileDescriptor(IType):
	''' 协议文件
	'''
	def __init__(self, fileName, fullPath):
		super(FileDescriptor, self).__init__(fileName, "file")
		self.fileName = fileName
		self.fullPath = fullPath
		self.includes = []
		self.packageName = None
		self.syntax = "proto2";

	@property
	def fullName(self):
		return self.packageName

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
		self.configCache = {}

	def isFileParsed(self, fileName):
		return fileName in self.files

	def getFileDescriptor(self, fileName):
		return self.files.get(fileName)

	def newFileDescriptor(self, fileName, fullPath):
		assert(fileName not in self.files)

		fd = FileDescriptor(fileName, fullPath)
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

	def getMessageConfig(self, name):
		return self.configCache.setdefault(name, {})

	def loadConfigCache(self, filePath):
		if not os.path.exists(filePath):
			self.configCache = {}
			return

		with open(filePath, "r", encoding="utf-8") as f:
			self.configCache = json.load(f)

	def saveConfigCache(self, filePath):
		with open(filePath, "w", encoding="utf-8", newline="\n") as f:
			json.dump(self.configCache, f, indent = 4, sort_keys = True)


ATTR_KEYS = ["mode", "cmd", "method"]

class Attribute(object):
	'''消息属性。'//@'开头的行，格式::

		[mode, cmd, method, key=value, ...]

	'''
	def __init__(self, id = 0):
		self.id = id
		self.index = 0
		self.attributes = {}
		self.isAutoCMD = False

	def addSingleValue(self, value):
		''' 添加值属性。会根据索引位置，自动转换成键-值对格式
		'''
		if self.index >= len(ATTR_KEYS):
			raise ValueError("invliad attribute: %s" % str(value))

		# 如果未指定协议号，则自动生成
		if self.index == 1 and isinstance(value, str):
			self.addPairValue("cmd", self.id)
			self.isAutoCMD = True
			self.index += 1

		key = ATTR_KEYS[self.index]
		self.index += 1
		self.addPairValue(key, value)

	def addPairValue(self, key, value):
		''' 添加键-值对属性
		'''
		self.attributes[key] = value

	def updatePairValue(self, key, value):
		self.attributes[key] = value
