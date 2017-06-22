# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
-- from $inputFile
local $moduleName = loadprotobuf "$moduleName"
"""

# args:  fields, method, moduleName, className, send, cmd
EXPAND_METHOD = """
#set argText = "network"
#if len($fields) > 0
#set argText = $argText + ", " + ", ".join($fields)
#end if
local function ${method}($argText)
	local proto = $moduleName.${className}()
#for field in $fields
	proto.$field = $field
#end for
	network:${send}($cmd, proto)
end
"""

COLLAPSED_METHOD = """
local function ${method}(network, proto)
	network:${send}($cmd, proto)
end
"""

# args: functions
RETURN = """
return {
#for cmd, fun in $functions
	$fun = $fun,
#end for
}
"""
