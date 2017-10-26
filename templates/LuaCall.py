# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
-- from $fileName
local $moduleName = loadprotobuf "$fileName"
"""

# args:  fields, method, moduleName, className, send, cmd
EXPAND_METHOD = """
#if $comment
-- [$cmd] ${comment}
#else
-- [$cmd]
#end if
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
#if $comment
-- [$cmd] ${comment}
#else
-- [$cmd]
#end if
local function ${method}(network, proto)
	network:${send}($cmd, proto)
end
"""

# args: functions
RETURN = """
$functions.sort(key = lambda x: x[1])
return {
#for cmd, fun in $functions
	$fun = $fun,
#end for
}
"""
