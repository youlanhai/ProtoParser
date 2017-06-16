#-*- coding: utf-8 -*-

import string
import re

# token
T_NONE = 0

T_IDENTITY = 257
T_MESSAGE = 258
T_ENUM = 259
T_STRING = 260
T_IMPORT = 261
T_REQUIRED = 262
T_OPTIONAL = 263
T_REPEATED = 264
T_PACKAGE = 265
T_ATTRIBUTE = 266
T_NUMBER = 267
T_BOOLEAN = 268

KEYWORDS = {
	"message" 	: T_MESSAGE,
	"enum" 		: T_ENUM,
	"import" 	: T_IMPORT,
	"required" 	: T_REQUIRED,
	"optional" 	: T_OPTIONAL,
	"repeated" 	: T_REPEATED,
	"package" 	: T_PACKAGE,
}

VAR_NAME_LETTER = string.letters + string.digits + '_'
VAR_NAME_PATTERN = re.compile(r"^[_a-zA-Z]\w*$")

TOKEN_2_NAME = {
	T_IDENTITY 	: "identity",
	T_MESSAGE 	: "message",
	T_ENUM 		: "enum",
	T_STRING 	: "string",
	T_IMPORT 	: "import",
	T_REQUIRED 	: "required",
	T_OPTIONAL 	: "optional",
	T_REPEATED 	: "repeated",
	T_PACKAGE 	: "package",
	T_ATTRIBUTE : "attribute",
	T_NUMBER 	: "number",
	T_BOOLEAN 	: "boolean",
}

def token2str(tk):
	if type(tk) == str:
		return tk
	return TOKEN_2_NAME[tk]

# 词法分析器
class Lexer(object):
	def __init__(self, content):
		super(Lexer, self).__init__()
		self.content = content
		self.index = 0
		self.symbols = []
		self.line = 1
		self.column = 1
		self.isError = False
		self.lastValue = None

	def getchar(self):
		if self.index >= len(self.content): return None

		ch = self.content[self.index]
		self.column += 1
		self.index += 1

		return ch

	def ungetchar(self):
		assert(self.index > 0)
		self.index -= 1
		self.column -= 1

	def enterNextLine(self):
		self.line += 1
		self.column = 1

	def readIdentity(self):
		s = ''
		while True:
			ch = self.getchar()
			if ch is None:
				break

			if ch not in VAR_NAME_LETTER:
				self.ungetchar()
				break
			s += ch

		if VAR_NAME_PATTERN.match(s):
			return s
		else:
			self.column -= len(s)
			return self.error('invalid identity name "%s"' % s)

	def readComment(self):
		ret = []
		while True:
			ch = self.getchar()
			if ch == '\n' or ch is None:
				break
			ret.append(ch)
		self.enterNextLine()
		return "".join(ret)

	def readString(self):
		s = ''
		while True:
			ch = self.getchar()
			if ch == '\n' or ch is None: return self.error('invalid string')
			if ch == '"': break
			s += ch
		return s

	def next(self):
		self.lastValue = None

		while True:
			ch = self.getchar()
			if ch is None:
				break

			elif ch == '\n':
				self.enterNextLine()

			elif ch in string.whitespace:
				pass

			elif ch == '/':
				ch = self.getchar()
				if ch != '/': # `//`
					self.error("invalid comment")
					break

				ch = self.getchar()
				if ch == '@': # `//@`
					return T_ATTRIBUTE

				else:
					self.ungetchar()
					self.readComment()

			elif ch == '"':
				self.lastValue = self.readString()
				if self.lastValue is None:
					break
				return T_STRING

			elif ch in '={}<>,;[]':
				return ch

			elif ch in '+-':
				ch = self.getchar()
				if ch in string.digits:
					self.ungetchar()
					self.lastValue = self.readNumber()
					return T_NUMBER

				else:
					self.error("invalid symbol '%s'" % ch)

			elif ch in string.digits:
				self.ungetchar()
				self.lastValue = self.readNumber()
				return T_NUMBER

			elif ch in VAR_NAME_LETTER:
				self.ungetchar()
				value = self.readIdentity()

				if value == "true":
					self.lastValue = True
					return T_BOOLEAN

				elif value == "false":
					self.lastValue = False
					return T_BOOLEAN

				if value is None:
					break

				else:
					self.lastValue = value
					return KEYWORDS.get(value, T_IDENTITY)

			else:
				self.error("invalid symbols '%s'" % ch)
				break

		return None

	def error(self, msg):
		self.isError = True
		print "error: line=%d, column=%d, %s" % (self.line, self.column, msg)

	def readNumber(self):
		ret = []

		ch = self.getchar()
		if ch in '+-':
			ret.append(ch)
			ch = self.getchar()

		while ch in string.digits:
			ret.append(ch)
			ch = self.getchar()

		if ch == '.':
			ret.append('.')
			ch = self.getchar()

			while ch in string.digits:
				ret.append(ch)
				ch = self.getchar()

		if ch in 'eE':
			ret.append(ch)
			ch = self.getchar()

			if ch in '+-':
				ret.append(ch)
				ch = self.getchar()

			while ch in string.digits:
				ret.append(ch)
				ch = self.getchar()

		self.ungetchar()

		value = "".join(ret)
		# print "readNumber", value
		return eval(value)

