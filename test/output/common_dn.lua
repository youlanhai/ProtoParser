--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"


local function broadcastPosition(network, x, y, z)
	local proto = common.Vector3()
	proto.x = x
	proto.y = y
	proto.z = z
	network:sendToOthers(2, proto)
end


local function teleportTo(network, x, y, z)
	local proto = common.Vector3()
	proto.x = x
	proto.y = y
	proto.z = z
	network:sendToAll(3, proto)
end


return {
	broadcastPosition = broadcastPosition,
	teleportTo = teleportTo,
}
