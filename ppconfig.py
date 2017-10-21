# -*- coding: utf-8 -*-

# 下面是一些通用的宏，拼接路径字符串的时候可以使用：
# OUTPUT_PATH : 输出的文件夹路径
# NAME : 输入文件的名称
# SOURCE_FILE : 输入文件的全名

#: 代码生成器配置
CODE_GENERATORS = [
	{
		# 上下行模式。和协议(message)属性中的上下行模式一致的消息，才会执行生成，
		"mode" : "up",

		# 代码生成器类名。位于generators模块中
		"class" : "NormalGenerator",

		# 模板模块名。位于templates模块中
		"template" : "LuaCall",

		# 输出文件的路径。
		"output" : "${OUTPUT_PATH}/${NAME}_up.lua",
	},
	{
		"mode" : "dn",
		"class" : "NormalGenerator",
		"template" : "LuaCall",
		"output" : "${OUTPUT_PATH}/${NAME}_dn.lua",
	},
]

#: 针对工程的生成器配置
PROJECT_GENERATORS = []

MAX_EXPAND_ARGS = 5

def custom_init():
	pass
