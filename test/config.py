# -*- coding: utf-8 -*-

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
	{
		"mode" : "up",
		"class" : "NormalGenerator",
		"template" : "LuaOnCall",
		"output" : "${OUTPUT_PATH}/${NAME}_up_on.lua",
	},
	{
		"mode" : "dn",
		"class" : "NormalGenerator",
		"template" : "LuaOnCall",
		"output" : "${OUTPUT_PATH}/${NAME}_dn_on.lua",
	},
	{
		"class" : "ListGenerator",
		"template" : "LuaList",
		"output" : "${OUTPUT_PATH}/${NAME}_list.lua",
	},
]

#: 针对工程的生成器配置
PROJECT_GENERATORS = [
	{
		"class" : "PackageGenerator",
		"template" : "LuaPackage",
		"output" : "${OUTPUT_PATH}/${NAME}.lua",
	}
]
