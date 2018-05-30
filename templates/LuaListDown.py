# -*- coding: utf-8 -*-
from LuaCommon import genOnName

TEMPLATE = """
-- this file is auto generate by ProtoParser tool.

$dn_messages.sort(key = lambda x: x[0])

local send_messages = {
#for cmd, mode, method, protoName in $dn_messages
	[$cmd] = "$method",
#end for
}

local recv_messages = {
#for cmd, mode, method, protoName in $dn_messages
#set onName = $genOnName($method)
	[$cmd] = "$onName",
#end for
}

return {
	recv_messages = recv_messages,
	send_messages = send_messages,
}
"""
