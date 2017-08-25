#-*- coding: utf-8 -*-

import lexer
import codes
import os

from lexer import token2str

VALID_ATTRIBUTE_TOKENS = (lexer.T_IDENTITY, lexer.T_STRING, lexer.T_NUMBER, lexer.T_BOOLEAN)
VALID_QUALIFIER_TOKENS = (lexer.T_REQUIRED, lexer.T_OPTIONAL, lexer.T_REPEATED)

class PParser(object):
	''' 语法分析器
	'''
	def __init__(self, module, fileName):
		super(PParser, self).__init__()
		self.module = module
		self.fd = self.module.newFileDescriptor(fileName)
		self.lexer = None

		self.lastAttributes = []

	def parse(self):
		print "parse:", self.fd.fileName

		with open(self.fd.fileName, "r") as f:
			self.lexer = lexer.Lexer(f.read())

		tokenHandler = {
			lexer.T_MESSAGE : self.parseMessage,
			lexer.T_ENUM 	: self.parseEnum,
			lexer.T_IMPORT 	: self.parseImport,
			lexer.T_ATTRIBUTE : self.parseAttribute,
			';' : self.parseEmpty,
		}

		token = self.lexer.next()
		while token is not None:
			handler = tokenHandler.get(token)
			if handler is None:
				self.error("Parser", "invalid token '%s'" % token2str(token))

			handler()
			token = self.lexer.next()

		self.lexer = None

	def matchNext(self, token, desc):
		self.matchToken(self.lexer.next(), token, desc)

	def matchToken(self, given, expected, desc):
		if given != expected:
			self.error(desc, "token '%s' expected, but '%s' was given." % (token2str(expected), token2str(given)))
		return

	def parseEmpty(self):
		pass

	def parseMessage(self):
		desc = "message"

		attributes = [attr.attributes for attr in self.lastAttributes]
		self.lastAttributes = []

		self.matchNext(lexer.T_IDENTITY, desc)

		name = self.lexer.lastValue
		if self.fd.isTypeExist(name):
			self.error(desc, "type '%s' has been exist." % name)

		cls = codes.ClassDescriptor(name, "message")
		cls.setAttributes(attributes)
		self.fd.addCode(cls)

		self.matchNext('{', desc)

		token = self.lexer.next()
		while token != None and token != '}':

			if token not in VALID_QUALIFIER_TOKENS:
				self.error(desc, "invalid token %s" % token2str(token))

			varQualifier = token2str(token)

			self.matchNext(lexer.T_IDENTITY, desc)
			varType = self.lexer.lastValue

			varTemplateArgs = None
			varName = None

			token = self.lexer.next()
			if token == '<':
				varTemplateArgs = self._parseTemplateArgs(desc)
				token = self.lexer.next()

			# self.matchToken(token, lexer.T_IDENTITY, desc)
			if not lexer.is_valid_identity(token):
				self.error(desc, "invalid token %s" % token2str(token))
			varName = self.lexer.lastValue

			self.matchNext('=', desc)

			self.matchNext(lexer.T_NUMBER, desc)
			varOrder = self.lexer.lastValue

			self.matchNext(';', desc)

			cls.addMember(varOrder, varQualifier, varName, varType, varTemplateArgs)

			token = self.lexer.next()

		self.matchToken(token, '}', desc)
		self.lastAttributes = []

	def parseEnum(self):
		self.error("enum", "doens't supported.")

	def parseImport(self):
		desc = "import"
		self.matchNext(lexer.T_STRING, desc)

		fname = self.lexer.lastValue

		for path in self.module.searchPath:
			fullPath = os.path.join(path, fname)
			if os.path.isfile(fullPath):
				self.loadIncludeFile(fname, fullPath)

		return

	def loadIncludeFile(self, name, fullPath):
		fd = self.module.files.get(fullPath)
		if fd:
			if not self.fd.addInclude(fd):
				self.error("import", "loop include '%s'" % name)
		else:
			pa = PParser(self.module, fullPath)
			if not self.fd.addInclude(pa.fd):
				self.error("import", "loop include '%s'" % name)

			pa.parse()
		return

	def _parseTemplateArgs(self, desc):
		ret = []

		token = self.lexer.next()
		while True:
			self.matchToken(token, lexer.T_IDENTITY, desc)

			varType = self.lexer.lastValue
			ret.append(varType)

			token = self.lexer.next()
			if token == '>':
				break

			elif token == ',':
				token = self.lexer.next()

			else:
				self.error(desc, "invalid token '%s'" % token2str(token))

		if len(ret) == 0:
			self.error(desc, "template args is empty.")

		return ret

	def error(self, desc, msg):
		msg = "error: line=%d, column=%d, %s: %s" % (self.lexer.line, self.lexer.column, desc, msg)
		raise RuntimeError, msg

	#属性 [mode, cmd, method, tag=value, ...]
	def parseAttribute(self):
		desc = "attribute"
		attr = codes.Attribute(self.module.allocateAttrID())

		self.matchNext('[', desc)

		token = self.lexer.next()
		while token != ']':

			if token not in VALID_ATTRIBUTE_TOKENS:
				self.error(desc, "invalid token '%s'" % token2str(token))
			value = self.lexer.lastValue

			token = self.lexer.next()
			if token == '=': # `key = value`
				token = self.lexer.next()
				if token not in VALID_ATTRIBUTE_TOKENS:
					self.error(desc, "invalid token '%s'" % token2str(token))

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
				self.error(desc, "token ',' was expected, but '%s' was given" % token2str(token))

		# print attr.attributes
		self.lastAttributes.append(attr)
