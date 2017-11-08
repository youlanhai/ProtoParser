#-*- coding: utf-8 -*-

import string
import re

# token
T_IDENTITY 	= 257
T_MESSAGE 	= 258
T_ENUM 		= 259
T_STRING 	= 260
T_IMPORT 	= 261
T_REQUIRED 	= 262
T_OPTIONAL 	= 263
T_REPEATED 	= 264
T_PACKAGE 	= 265
T_ATTRIBUTE = 266
T_NUMBER 	= 267
T_BOOLEAN 	= 268
T_SYNTAX 	= 269
T_OPTION 	= 270
T_PUBLIC 	= 271
T_WEAK 		= 272
T_EXTENSIONS = 274
T_RESERVED 	= 275
T_TO 		= 276
T_EXTEND 	= 277
T_MAP 		= 278

KEYWORDS = {
	"message" 	: T_MESSAGE,
	"enum" 		: T_ENUM,
	"import" 	: T_IMPORT,
	"required" 	: T_REQUIRED,
	"optional" 	: T_OPTIONAL,
	"repeated" 	: T_REPEATED,
	"package" 	: T_PACKAGE,
	"syntax" 	: T_SYNTAX,
	"option" 	: T_OPTION,
	"public" 	: T_PUBLIC,
	"weak" 		: T_WEAK,
	"extensions": T_EXTENSIONS,
	"reserved" 	: T_RESERVED,
	"to" 		: T_TO,
	"extend" 	: T_EXTEND,
	"map"		: T_MAP,
}

KEYWORD_TOKENS = set([tk for tk in KEYWORDS.itervalues()])

VAR_NAME_LETTER = string.letters + string.digits + '_'
VAR_NAME_PATTERN = re.compile(r"^[_a-zA-Z]\w*$")

TOKEN_2_NAME = {key : val for val, key in KEYWORDS.iteritems()}
TOKEN_2_NAME.update({
	T_IDENTITY 	: "identity",
	T_ATTRIBUTE : "attribute",
	T_STRING 	: "string",
	T_NUMBER 	: "number",
	T_BOOLEAN 	: "boolean",
})

def token2str(tk):
	if type(tk) == str:
		return tk
	return TOKEN_2_NAME[tk]

def is_keyword_token(tk):
	return tk in KEYWORD_TOKENS


# 词法分析器
class PLexer(object):
	def __init__(self, content, fileName):
		super(PLexer, self).__init__()
		self.fileName = fileName
		self.content = content
		self.index = 0
		self.line = 1
		self.column = 1

		self.token = None
		self.value = None

	def getchar(self):
		index = self.index
		self.index += 1

		if index >= len(self.content):
			return None

		ch = self.content[index]
		self.column += 1
		return ch

	def ungetchar(self):
		assert(self.index > 0)
		self.index -= 1
		self.column -= 1

	def enterNextLine(self):
		self.line += 1
		self.column = 1

	def readIdentity(self):
		ret = []

		ch = self.getchar()
		while ch is not None and ch in VAR_NAME_LETTER:
			ret.append(ch)
			ch = self.getchar()

		self.ungetchar()
		s = "".join(ret)
		if VAR_NAME_PATTERN.match(s):
			return s
		
		self.column -= len(s)
		self.error('invalid identity name "%s"' % s)

	def readBlockComment(self):
		ret = []

		startLine = self.line
		startColumn = self.column

		ch = self.getchar()
		while True:
			if ch is None:
				self.error('unclosed comment match line %d, column %d' % (startLine, startColumn))

			if ch == '*':
				chNext = self.getchar()
				if chNext is None:
					self.error("unclosed comment match line %d, column %d" % (startLine, startColumn))
				elif chNext == '/': # `*/`
					break # 唯一结束条件
				else:
					ret.append(ch)
					ch = chNext
			else:
				if ch == '\n':
					self.enterNextLine()

				ret.append(ch)
				ch = self.getchar()

		return "".join(ret)


	def readLineComment(self):
		ret = []

		ch = self.getchar()
		while ch != '\n' and ch is not None:
			ret.append(ch)
			ch = self.getchar()

		self.enterNextLine()
		return "".join(ret)

	def readString(self):
		ret = []
		ch = self.getchar()
		while ch != '"':
			if ch == '\n' or ch is None:
				self.error('invalid string')

			ret.append(ch)
			ch = self.getchar()

		return "".join(ret)

	def next(self):
		token = self.parseToken()
		self.token = token
		return token

	def parseToken(self):
		self.value = None

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
				if ch == '*': # `/* */`
					self.readBlockComment()

				elif ch == '/': # `//`
					ch = self.getchar()
					if ch == '@': # `//@`
						return T_ATTRIBUTE

					else:
						self.ungetchar()
						self.readLineComment()
				else:
					self.error("invalid symbol '%s'" % ch)

			elif ch == '"':
				self.value = self.readString()
				if self.value is None:
					break
				return T_STRING

			elif ch in '.={}<>,;[]()':
				return ch

			elif ch in '+-':
				ch = self.getchar()
				if ch in string.digits:
					self.ungetchar()
					self.value = self.readNumber()
					return T_NUMBER

				else:
					self.error("invalid symbol '%s'" % ch)

			elif ch in string.digits:
				self.ungetchar()
				self.value = self.readNumber()
				return T_NUMBER

			elif ch in VAR_NAME_LETTER:
				self.ungetchar()
				value = self.readIdentity()

				if value == "true":
					self.value = True
					return T_BOOLEAN

				elif value == "false":
					self.value = False
					return T_BOOLEAN

				if value is None:
					break

				else:
					self.value = value
					return KEYWORDS.get(value, T_IDENTITY)

			else:
				self.error("invalid symbol '%s'" % ch)
				break

		return None

	def error(self, msg):
		self.isError = True
		msg = "error: file '%s', line=%d, column=%d, %s" % (self.fileName, self.line, self.column, msg)
		raise RuntimeError, msg

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
		return eval(value)

