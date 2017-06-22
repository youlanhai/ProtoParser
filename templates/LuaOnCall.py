# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
-- from $inputFile
local $moduleName = loadprotobuf "$moduleName"
"""

EXPAND_METHOD = """
local function ${method}(data)
	local proto = $moduleName.${className}()
	proto:Parse(data)

	#set values = ["proto." + v for v in $fields]
	#set argText = ", ".join($values)
	return "${method}", proto, {$argText}
end
"""

COLLAPSED_METHOD = """
local function ${method}(data)
	local proto = $moduleName.${className}()
	proto:Parse(data)

	return "${method}", proto, {}
end
"""

RETURN = """
return {
#for cmd, fun in $functions
	[$cmd] = $fun,
#end for
}
"""
