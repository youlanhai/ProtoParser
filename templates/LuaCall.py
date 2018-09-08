# -*- coding: utf-8 -*-

HEADER = """--
-- this file is auto generate by ProtoParser tool.
local Network = {}
"""

BEGIN = """
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
#set argText = ", ".join($fields)
function Network:${method}($argText)
	local proto = $moduleName.${className}()
#for field in $fields
	proto.$field = $field
#end for
	return self:${send}($cmd, proto)
end
"""

COLLAPSED_METHOD = """
#if $comment
-- [$cmd] ${comment}
#else
-- [$cmd]
#end if
function Network:${method}(proto)
	return self:${send}($cmd, proto)
end
"""

# args: functions
RETURN = """
return Network
"""
