#-*- coding: utf-8 -*-

import lexer
import codes
import os

from lexer import token2str

VALID_ATTRIBUTE_TOKENS = (lexer.T_IDENTITY, lexer.T_STRING, lexer.T_NUMBER, lexer.T_BOOLEAN)

# 语法分析器
class Parser(object):
	def __init__(self, module, fileName):
		super(Parser, self).__init__()
		self.isError = False
		self.module = module
		self.fd = self.module.newFileDescriptor(fileName)
		self.lexer = None

		self.lastAttributes = []

	def parse(self):
		print "parse:", self.fd.fileName

		with open(self.fd.fileName, "r") as f:
			self.lexer = lexer.Lexer(f.read())

		while not self.isError:
			token = self.lexer.next()

			if token is None:
				break

			elif token == lexer.T_STRUCT:
				self.parseStruct()

			elif token == lexer.T_ENUM:
				self.parseEnum()

			elif token == lexer.T_IMPORT:
				self.parseImport()

			elif token == lexer.T_ATTRIBUTE:
				self.parseAttribute()

			elif token == ';':
				pass

			else:
				self.error("invalid token '%s'" % token2str(token))

		self.lexer = None
		return True

	def matchNext(self, token, desc):
		return self.matchToken(self.lexer.next(), token, desc)

	def matchToken(self, src, dst, desc):
		if src != dst:
			self.error("%s: invalid token '%s', token '%s' needed." % (desc, token2str(src), token2str(dst)))
			return False
		return True

	def validType(self, type, desc):
		varType = self.lexer.lastValue
		if not codes.isBuiltin(varType) and not self.fd.isTypeExist(varType):
			self.error("%s: invalid type '%s'" % (desc, varType))
			return False
		return True

	def parseStruct(self):
		desc = "message"

		attributes = [attr.attributes for attr in self.lastAttributes]
		self.lastAttributes = []

		if not self.matchNext(lexer.T_IDENTITY, desc):
			return False

		name = self.lexer.lastValue
		if self.fd.isTypeExist(name):
			self.error("%s : type '%s' has been exist." % (desc, name))
			return False

		cls = codes.ClassDescriptor(name, "message")
		cls.setAttributes(attributes)
		self.fd.addCode(cls)

		if not self.matchNext('{', desc):
			return False

		token = self.lexer.next()
		while token != None and token != '}':

			if token not in (lexer.T_REQUIRED, lexer.T_OPTIONAL, lexer.T_REPEATED):
				print self.lexer.lastValue
				self.error("%s: invalid token %s" % (desc, token2str(token)))
				return False

			varQualifier = token2str(token)
			
			if not self.matchNext(lexer.T_IDENTITY, desc):
				return False

			varType = self.lexer.lastValue
			varTemplateArgs = None
			varName = None

			token = self.lexer.next()
			if token == '<':
				varTemplateArgs = self._parseTemplateArgs(desc)
				if varTemplateArgs is None:
					return False

				token = self.lexer.next()

			if not self.matchToken(token, lexer.T_IDENTITY, desc):
				return False

			varName = self.lexer.lastValue

			if not self.matchNext('=', desc):
				return False

			if not self.matchNext(lexer.T_NUMBER, desc):
				return False
			varOrder = self.lexer.lastValue

			if not self.matchNext(';', desc):
				return False

			cls.addMember(varOrder, varQualifier, varName, varType, varTemplateArgs)

			# print "> %s %s %s = %s" % (varQualifier, varType, varName, varOrder)

			token = self.lexer.next()

		if not self.matchToken(token, '}', desc):
			return False

		self.lastAttributes = []
		return True

	def parseEnum(self):
		self.error("enum: doens't supported.")

	def parseImport(self):
		desc = "import"
		if not self.matchNext(lexer.T_STRING, desc): return False
		fname = self.lexer.lastValue

		for path in self.module.searchPath:
			fullPath = os.path.join(path, fname)
			if os.path.isfile(fullPath):
				return self.loadIncludeFile(fname, fullPath)

		self.error("import failed. the file '%s' was not found" % fname)

	def loadIncludeFile(self, name, fullPath):
		fd = self.module.files.get(fullPath)
		if fd is not None:
			if self.fd.addInclude(fd):
				return True
			else:
				return self.error("import failed. loop include '%s'" % name)
		
		pa = Parser(self.module, fullPath)
		if not self.fd.addInclude(pa.fd):
			return self.error("import failed. loop include '%s'" % name)

		if not pa.parse():
			return self.error("import failed. failed to load file '%s'" % fullPath)

		return True

	def _parseTemplateArgs(self, desc):
		ret = []

		token = self.lexer.next()
		while True:
			if not self.matchToken(token, lexer.T_IDENTITY, desc):
				return None

			varType = self.lexer.lastValue
			if not self.validType(varType, desc):
				return None

			ret.append(varType)

			token = self.lexer.next()
			if token == '>':
				break

			elif token == ',':
				token = self.lexer.next()

			else:
				self.error("%s: invalid token '%s'" % (desc, token2str(token), ))
				return None

		if len(ret) == 0:
			self.error("%s: empty template args." % desc)
			return None

		return ret

	def error(self, msg):
		self.isError = True
		msg = "error: line=%d, column=%d, %s" % (self.lexer.line, self.lexer.column, msg)
		raise RuntimeError, msg

	#属性 [mode, cmd, method, tag=value, ...]
	def parseAttribute(self):
		desc = "attribute"
		attr = codes.Attribute()

		self.matchNext('[', desc)

		token = self.lexer.next()
		while token != ']':

			if token not in VALID_ATTRIBUTE_TOKENS:
				self.error("%s: invalid token '%s'" % (desc, token2str(token)))
			value = self.lexer.lastValue

			token = self.lexer.next()
			if token == '=': # `key = value`
				token = self.lexer.next()
				if token not in VALID_ATTRIBUTE_TOKENS:
					self.error("%s: invalid token '%s'" % (desc, token2str(token)))

				value2 = self.lexer.lastValue
				attr.addPairValue(value, value2)

				token = self.lexer.next()
			else: # `value, `
				attr.addSingleValue(value)

			if token == ']':
				break

			elif token == ',':
				token = self.lexer.next()

			else:
				self.error("%s: symbol ',' was expected, but '%s' was given" % (desc, token2str(token)))

		# print attr.attributes
		self.lastAttributes.append(attr)
		return
