# -*- coding: utf-8 -*-

TEMPLATE = """
-- this file is auto generate by ProtoParser tool.

$up_messages.sort(key = lambda x: x[0])
local up_messages = {
#for cmd, mode, method, protoName in $up_messages
	[$cmd] = "$method",
#end for
}

$dn_messages.sort(key = lambda x: x[0])
local dn_messages = {
#for cmd, mode, method, protoName in $dn_messages
	[$cmd] = "$method",
#end for
}

return {
	up_messages = up_messages,
	dn_messages = dn_messages,
}
"""
