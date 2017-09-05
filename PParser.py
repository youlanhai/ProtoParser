#-*- coding: utf-8 -*-

import lexer
import codes
import os

from lexer import token2str

VALID_VALUE_TOKENS = (lexer.T_IDENTITY, lexer.T_STRING, lexer.T_NUMBER, lexer.T_BOOLEAN)
VALID_QUALIFIER_TOKENS = (lexer.T_REQUIRED, lexer.T_OPTIONAL, lexer.T_REPEATED)

def is_expected_token(given, expected):
	if isinstance(expected, int) or isinstance(expected, str):
		return given == expected

	return given in expected

def is_identity_token(token):
	return token == lexer.T_IDENTITY or lexer.is_keyword_token(token)


class TokenInfo:
	def __init__(self, lexer):
		self.line = lexer.line
		self.column = lexer.column
		self.token = lexer.token
		self.value = lexer.value


class PParser(object):
	''' 语法分析器
	'''
	def __init__(self, module, fileName):
		super(PParser, self).__init__()
		self.module = module
		self.fd = self.module.newFileDescriptor(fileName)
		self.lexer = None

		self.lastAttributes = []

		self.tokenInfo = None
		self.aheadTokenInfo = None

	def nextToken(self, includeBlank = False):
		if self.aheadTokenInfo:
			self.tokenInfo = self.aheadTokenInfo
			self.aheadTokenInfo = None
		else:
			self.lexer.next(includeBlank)
			self.tokenInfo = TokenInfo(self.lexer)
		return self.tokenInfo.token

	def lookAhead(self, includeBlank = False):
		if not self.aheadTokenInfo:
			self.lexer.next(includeBlank)
			self.aheadTokenInfo = TokenInfo(self.lexer)
		return self.aheadTokenInfo.token

	def parse(self):
		print "parse:", self.fd.fileName

		with open(self.fd.fileName, "r") as f:
			self.lexer = lexer.Lexer(f.read())

		tokenHandler = {
			';' : self.parseEmpty,
		}

		token = self.nextToken()
		while token is not None:
			handler = None

			if lexer.is_keyword_token(token):
				funName = "parse_" + lexer.token2str(token)
				handler = getattr(self, funName, None)

			if handler is None:
				handler = tokenHandler.get(token)

			if handler is None:
				self.error("Parser", "invalid token '%s'" % token2str(token))

			handler()
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

	def parseEmpty(self):
		pass

	def parse_message(self, append = False):
		desc = "message"

		attributes = [attr.attributes for attr in self.lastAttributes]
		self.lastAttributes = []

		name = self._parseIdentity(desc)
		cls = None
		if append:
			cls = self.fd.findType(name)

		else:
			if self.fd.isTypeExist(name):
				self.error(desc, "type '%s' has been exist." % name)

			cls = codes.ClassDescriptor(name, "message")
			cls.setAttributes(attributes)
			self.fd.addCode(cls)

		self.matchNext('{', desc)

		token = self.nextToken()
		while token != None and token != '}':

			if token not in VALID_QUALIFIER_TOKENS:
				self.error(desc, "invalid token %s" % token2str(token))

			varQualifier = token2str(token)
			varType = self._parseFullIdentity(desc)

			varTemplateArgs = None
			varName = None

			token = self.lookAhead()
			if token == '<':
				varTemplateArgs = self._parseTemplateArgs(desc)

			varName = self._parseIdentity(desc)

			self.matchNext('=', desc)

			self.matchNext(lexer.T_NUMBER, desc)
			varOrder = self.tokenInfo.value

			token = self.nextToken()
			if token == '[':
				self._parseFiledOption(desc)

			self.matchToken(token, ';', desc)
			cls.addMember(varOrder, varQualifier, varName, varType, varTemplateArgs)

			token = self.nextToken()

		self.matchToken(token, '}', desc)
		self.lastAttributes = []

	def _parseFiledOption(self, desc):
		while True:
			self.matchNext(lexer.T_IDENTITY, desc)
			self.matchNext('=', desc)
			self.matchNext(VALID_VALUE_TOKENS, desc)

			token = self.nextToken()
			if token == ']':
				break

			self.matchToken(token, ',', desc)
		return

	def parse_enum(self):
		desc = "enum"
		name = self._parseIdentity(desc)
		self.matchNext('{', desc)

		token = self.nextToken()
		while token != None and token != '}':
			self.matchIdentity(token, desc)
			fieldName = self.tokenInfo.value

			self.matchNext('=', desc)
			self.matchNext(lexer.T_NUMBER, desc)

			token = self.nextToken()
			if token == '}':
				break

			self.matchToken(token, ';', desc)
			token = self.nextToken()

		self.matchToken(token, '}', desc)

	def parse_import(self):
		desc = "import"

		token = self.nextToken()
		if token in (lexer.T_PUBLIC, lexer.T_WEAK):
			token = self.nextToken()

		self.matchToken(token, lexer.T_STRING, desc)
		fname = self.tokenInfo.value


		fullPath = self.module.findFileFullPath(fname)
		if fullPath is None:
			raise RuntimeError, "import: Failed find file '%s'" % fname

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
		msg = "error: line=%d, column=%d, %s: %s" % (self.tokenInfo.line, self.tokenInfo.column, desc, msg)
		raise RuntimeError, msg

	#属性 [mode, cmd, method, tag=value, ...]
	def parse_attribute(self):
		desc = "attribute"
		attr = codes.Attribute(self.module.allocateAttrID())

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

	def parse_package(self):
		desc = "package"

		name = self._parseFullIdentity(desc)
		return

	def parse_syntax(self):
		desc = "syntax"
		self.matchNext('=', desc)
		self.matchNext(lexer.T_STRING, desc)

		if self.tokenInfo.value != "proto2":
			self.error(desc, "only 'proto2' was supported. but '%s' was given", self.tokenInfo.value)

		return

	def parse_option(self):
		desc = "option"

		name = None
		prefixToken = self.lookAhead()
		if prefixToken == '(':
			self.nextToken()
			name = self._parseFullIdentity(desc)
			self.matchNext(')', desc)
		else:
			name = self._parseFullIdentity(desc)

		self.matchNext('=', desc)
		self.matchNext(VALID_VALUE_TOKENS, desc)

	def parse_extend(self):
		self.parse_message(True)
