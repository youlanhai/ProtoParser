# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
-- from $inputFile
"""

EXPAND_METHOD = """
local function ${method}(network, data)
	local proto = $moduleName.${className}()
	proto:Parse(data)
	#set values = ["proto." + v for v in $fields]
	#set argText = ", ".join($values)
	network:oncall_${method}($argText)
end
"""

COLLAPSED_METHOD = """
local function ${method}(network, data)
	local proto = $moduleName.${className}()
	proto:Parse(data)
	network:oncall_${method}(proto)
end
"""

RETURN = """
return {
#for cmd, fun in $functions
	[$cmd] = $fun,
#end for
}
"""
