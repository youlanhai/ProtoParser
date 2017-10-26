
-- this file is auto generate by ProtoParser tool.


local up_messages = {
	[1] = "sendPosition",
	[6] = "sendTransform",
	[1000] = "setRotation",
	[1001] = "login",
}


local dn_messages = {
	[2] = "broadcastPosition",
	[3] = "teleportTo",
	[7] = "onTransformChanged",
}

return {
	up_messages = up_messages,
	dn_messages = dn_messages,
}
