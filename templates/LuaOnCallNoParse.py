# -*- coding: utf-8 -*-
from LuaCommon import genOnName

HEADER = """--
-- this file is auto generate by ProtoParser tool.
local EMPTY_TABLE = {}
local Module = {}
"""

BEGIN = """
-- from $fileName
local $moduleName = loadprotobuf "$fileName"
"""

EXPAND_METHOD = """
#if $comment
-- ${comment}
#end if
#set onName = $genOnName($method)
-- ${onName}
Module[$cmd] = function(proto)
	#set values = ["proto." + v for v in $fields]
	#set argText = ", ".join($values)
	return proto, {$argText}
end
"""

COLLAPSED_METHOD = """
#if $comment
-- [${comment}
#end if
#set onName = $genOnName($method)
-- ${onName}
Module[$cmd] = function(proto)
	return proto, EMPTY_TABLE
end
"""

RETURN = """
return Module
"""
