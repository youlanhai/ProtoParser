# -*- coding: utf-8 -*-

TEMPLATE = """
-- this file is auto generate by ProtoParser tool.

return {
#for cmd, mode, method, protoName in $messages
	{$cmd, "$mode", "$method", "$protoName"},
#end for
}
"""
