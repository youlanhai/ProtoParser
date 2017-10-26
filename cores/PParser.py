#-*- coding: utf-8 -*-
import os
import PCodes
import PLexer
from PLexer import token2str, is_keyword_token

VALID_VALUE_TOKENS = (
	PLexer.T_IDENTITY,
	PLexer.T_STRING,
	PLexer.T_NUMBER,
	PLexer.T_BOOLEAN
)

VALID_QUALIFIER_TOKENS = (
	PLexer.T_REQUIRED,
	PLexer.T_OPTIONAL,
	PLexer.T_REPEATED
)

def is_expected_token(given, expected):
	if isinstance(expected, int) or isinstance(expected, str):
		return given == expected

	return given in expected

def is_identity_token(token):
	return token == PLexer.T_IDENTITY or is_keyword_token(token)


class TokenInfo:
	def __init__(self, lexer):
		self.line = lexer.line
		self.column = lexer.column
		self.token = lexer.token
		self.value = lexer.value


class PParser(object):
	''' 语法分析器
	'''
	def __init__(self, module, fd):
		super(PParser, self).__init__()
		self.module = module
		self.fd = fd
		self.lexer = None

		self.lastAttributes = []

		self.tokenInfo = None
		self.aheadTokenInfo = None

	def nextToken(self):
		if self.aheadTokenInfo:
			self.tokenInfo = self.aheadTokenInfo
			self.aheadTokenInfo = None
		else:
			self.lexer.next()
			self.tokenInfo = TokenInfo(self.lexer)
		return self.tokenInfo.token

	def lookAhead(self):
		if not self.aheadTokenInfo:
			self.lexer.next()
			self.aheadTokenInfo = TokenInfo(self.lexer)
		return self.aheadTokenInfo.token

	def parse(self):
		print "parse:", self.fd.fileName

		with open(self.fd.fullPath, "r") as f:
			self.lexer = PLexer.PLexer(f.read(), self.fd.fileName)

		tokenHandler = {
			';' : self.parseEmpty,
		}

		token = self.nextToken()
		while token is not None:
			handler = None

			if is_keyword_token(token) or token in (PLexer.T_ATTRIBUTE, ):
				funName = "parse_" + token2str(token)
				handler = getattr(self, funName, None)

			if handler is None:
				handler = tokenHandler.get(token)

			if handler is None:
				self.error("Parser", "invalid token '%s'" % token2str(token))

			handler(self.fd)
			token = self.nextToken()

		self.lexer = None

	def matchNext(self, token, desc):
		self.matchToken(self.nextToken(), token, desc)

	def matchToken(self, given, expected, desc):
		ok = is_expected_token(given, expected)

		if ok: return

		tokeName = None
		if isinstance(expected, int):
			tokeName = token2str(expected)
		else:
			names = [token2str(tk) for tk in expected]
			tokeName = "|".join(names)
		self.error(desc, "token '%s' expected, but '%s' was given." % (tokeName, token2str(given)))
		return

	def parseEmpty(self, parent = None):
		pass

	def parse_message(self, parent = None, extend = False):
		desc = "message"

		attributes = self.lastAttributes
		self.lastAttributes = []

		name = self._parseFullIdentity(desc)
		cls = None
		if extend:
			cls = parent.findType(name)

		if cls is None:
			if parent.isTypeExist(name):
				self.error(desc, "type '%s' has been exist." % name)

			cls = PCodes.ClassDescriptor(name, parent)
			parent.addType(cls)

		self.matchNext('{', desc)

		token = self.nextToken()
		while token != None and token != '}':
			if token == ';':
				pass

			elif token == PLexer.T_MESSAGE:
				self.parse_message(parent = cls)

			elif token == PLexer.T_ENUM:
				self.parse_enum(parent = cls)

			elif token == PLexer.T_OPTION:
				self.parse_option(cls)

			elif token in VALID_QUALIFIER_TOKENS:
				self._parseMessageVarFiled(cls, desc)

			elif token == PLexer.T_EXTENSIONS:
				self._parseExtensions(cls)

			elif token == PLexer.T_RESERVED:
				self._parseReserved(cls)

			elif token == PLexer.T_EXTEND:
				self.parse_extend(parent = cls)

			else:
				self.error(desc, "invalid token %s" % token2str(token))

			token = self.nextToken()

		self.matchToken(token, '}', desc)
		self.lastAttributes = []

		cls.setAttributes(attributes)

	def _parseMessageVarFiled(self, cls, desc):
		token = self.tokenInfo.token

		varQualifier = token2str(token)
		varType = self._parseFullIdentity(desc)

		varTemplateArgs = None
		varName = None

		token = self.lookAhead()
		if token == '<':
			varTemplateArgs = self._parseTemplateArgs(desc)

		varName = self._parseIdentity(desc)

		self.matchNext('=', desc)

		self.matchNext(PLexer.T_NUMBER, desc)
		varOrder = self.tokenInfo.value

		token = self.lookAhead()
		if token == '[':
			self._parseFiledOption(desc)

		self.matchNext(';', desc)
		cls.addMember(varOrder, varQualifier, varName, varType, varTemplateArgs)

	def _parseFiledOption(self, desc):
		self.nextToken() # ignore '['
		while True:
			self.matchNext(PLexer.T_IDENTITY, desc)
			self.matchNext('=', desc)
			self.matchNext(VALID_VALUE_TOKENS, desc)

			token = self.nextToken()
			if token == ']':
				break

			self.matchToken(token, ',', desc)
		return

	def _parseRange(self, parent, desc):
		while True:
			self.matchNext(PLexer.T_NUMBER, desc)
			litMin = self.tokenInfo.value
			litMax = None

			token = self.nextToken()
			if token == PLexer.T_TO:
				token = self.nextToken()
				if token == PLexer.T_NUMBER:
					litMax = self.tokenInfo.value
				elif token == PLexer.T_IDENTITY and self.tokenInfo.value == "max":
					pass
				else:
					self.error(desc, "invalid token '%s'" % token2str(token))

				token = self.nextToken()

			if token == ';':
				break

			self.matchToken(token, ',', desc)
		return

	def _parseFieldList(self, parent, desc):
		while True:
			self.matchNext(PLexer.T_STRING, desc)

			token = self.nextToken()
			if token == ';':
				break

			self.matchToken(token, ',', desc)
		return

	def _parseExtensions(self, parent):
		''' extensions = "extensions" ranges ";"
			ranges = range { "," range }
			range =  intLit [ "to" ( intLit | "max" ) ]
		'''
		desc = "extensions"
		self._parseRange(parent, desc)
		return

	def _parseReserved(self, parent):
		'''	reserved = "reserved" ( ranges | fieldNames ) ";"
			fieldNames = fieldName { "," fieldName }
		'''
		desc = "reserved"
		token = self.lookAhead()
		if token == PLexer.T_NUMBER:
			self._parseRange(parent, desc)

		elif token == PLexer.T_STRING:
			self._parseFieldList(parent, desc)

		return

	def parse_enum(self, parent = None):
		desc = "enum"
		name = self._parseIdentity(desc)
		self.matchNext('{', desc)

		enum = PCodes.EnumDescriptor(name)
		parent.addType(enum)

		token = self.nextToken()
		sequenceID = 0
		while token != None and token != '}':
			self.matchIdentity(token, desc)
			fieldName = self.tokenInfo.value
			fieldValue = None

			token = self.nextToken()
			if token == '=':
				token = self.matchNext(PLexer.T_NUMBER, desc)
				fieldValue = self.tokenInfo.value
				sequenceID = fieldValue + 1
			else:
				fieldValue = sequenceID
				sequenceID += 1

			enum.addField(fieldName, fieldValue)

			token = self.nextToken()
			if token == '}':
				break

			self.matchToken(token, ';', desc)
			token = self.nextToken()

		self.matchToken(token, '}', desc)

	def parse_import(self, parent = None):
		desc = "import"

		token = self.nextToken()
		if token in (PLexer.T_PUBLIC, PLexer.T_WEAK):
			token = self.nextToken()

		self.matchToken(token, PLexer.T_STRING, desc)
		fname = self.tokenInfo.value

		fileName = None
		fullPath = None

		curPath = os.path.dirname(self.fd.fileName)
		if len(curPath) > 0:
			fileName = os.path.join(curPath, fname)
			fullPath = self.module.findFileFullPath(fileName)

		if fullPath is None:
			fileName = fname
			fullPath = self.module.findFileFullPath(fileName)

		if fullPath is None:
			raise RuntimeError, "import: Failed find file '%s'" % fname

		self.loadIncludeFile(fileName, fullPath)
		return

	def loadIncludeFile(self, fileName, fullPath):
		fileName = fileName.replace('\\', '/')
		fd = self.module.files.get(fileName)
		if fd:
			if not self.fd.addInclude(fd):
				self.error("import", "loop include '%s'" % fileName)
		else:
			fd = self.module.newFileDescriptor(fileName, fullPath)
			pa = PParser(self.module, fd)
			if not self.fd.addInclude(pa.fd):
				self.error("import", "loop include '%s'" % fileName)

			pa.parse()
		return

	def _parseTemplateArgs(self, desc):
		''' 语法格式:
		template = '<' t_args '>'
		t_args = full_identity {',' t_args }
		'''
		ret = []

		self.nextToken() # ignore '<'
		while True:
			varType = self._parseFullIdentity(desc)
			ret.append(varType)

			token = self.lookAhead()
			if token == '>':
				break

			self.matchNext(',', desc)

		self.nextToken() # ignore '>'

		if len(ret) == 0:
			self.error(desc, "template args is empty.")

		return ret

	def error(self, desc, msg):
		msg = "error: file '%s', line=%d, column=%d, %s: %s" % (
			self.fd.fileName, self.tokenInfo.line, self.tokenInfo.column, desc, msg)
		raise RuntimeError, msg

	#属性 [mode, cmd, method, tag=value, ...]
	def parse_attribute(self, parent = None):
		desc = "attribute"
		attr = PCodes.Attribute(self.module.allocateAttrID())

		self.matchNext('[', desc)

		token = self.nextToken()
		while token != ']':

			if token not in VALID_VALUE_TOKENS:
				self.error(desc, "invalid token '%s'" % token2str(token))
			value = self.tokenInfo.value

			token = self.nextToken()
			if token == '=': # `key = value`
				token = self.nextToken()
				if token not in VALID_VALUE_TOKENS:
					self.error(desc, "invalid token '%s'" % token2str(token))

				value2 = self.tokenInfo.value
				attr.addPairValue(value, value2)

				token = self.nextToken()
			else: # `value, `
				attr.addSingleValue(value)

			if token == ']':
				break

			elif token == ',':
				token = self.nextToken()

			else:
				self.error(desc, "token ',' was expected, but '%s' was given" % token2str(token))

		# print attr.attributes
		self.lastAttributes.append(attr)

	def matchIdentity(self, token, desc):
		if not is_identity_token(token):
			self.error(desc, "identity expected, but '%s' was given" % token2str(token))
		
		return

	def _parseIdentity(self, desc):
		token = self.nextToken()
		self.matchIdentity(token, desc)
		return self.tokenInfo.value

	def _parseFullIdentity(self, desc):
		''' 解析一个变量的全名。bnf格式如：name = identity { '.' name }
			@param desc 		当前要为什么类型的语句解析符号，用于出错时打印log
			@return 返回变量全名。如: xxx 或 xxx.yyy的形式
		'''
		name = ""
		while True:
			name += self._parseIdentity(desc)

			token = self.lookAhead()
			if token != '.':
				break

			self.nextToken()
			name += '.'

		return name

	def parse_package(self, parent = None):
		desc = "package"

		name = self._parseFullIdentity(desc)
		self.fd.setPackageName(name)
		return

	def parse_syntax(self, parent = None):
		desc = "syntax"
		self.matchNext('=', desc)
		self.matchNext(PLexer.T_STRING, desc)

		syntax = self.tokenInfo.value
		if syntax != "proto2":
			self.error(desc, "only 'proto2' was supported. but '%s' was given", syntax)

		self.fd.setSyntax(syntax)
		return

	def parse_option(self, parent = None):
		desc = "option"

		name = None
		value = None
		prefixToken = self.lookAhead()
		if prefixToken == '(':
			self.nextToken()
			name = self._parseFullIdentity(desc)
			self.matchNext(')', desc)
		else:
			name = self._parseFullIdentity(desc)

		self.matchNext('=', desc)
		self.matchNext(VALID_VALUE_TOKENS, desc)
		value = self.tokenInfo.value

		parent.addOption(name, value)

	def parse_extend(self, parent = None):
		self.parse_message(parent, True)
