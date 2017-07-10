# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
-- from $inputFile
local $moduleName = loadprotobuf "$moduleName"
"""

def genOnName(name):
	if name.startswith("on"):
		return name
	return "on" + name[0].upper() + name[1:]

EXPAND_METHOD = """
#set onName = $genOnName($method)
local function ${onName}(data)
	local proto = $moduleName.${className}()
	proto:Parse(data)

	#set values = ["proto." + v for v in $fields]
	#set argText = ", ".join($values)
	return "${onName}", proto, {$argText}
end
"""

COLLAPSED_METHOD = """
#set onName = $genOnName($method)
local function ${onName}(data)
	local proto = $moduleName.${className}()
	proto:Parse(data)

	return "${onName}", proto, {}
end
"""

RETURN = """
return {
#for cmd, fun in $functions
	[$cmd] = $fun,
#end for
}
"""
