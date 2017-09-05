--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"


local function onBroadcastPosition(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return "onBroadcastPosition", proto, {proto.x, proto.y, proto.z}
end


local function onTeleportTo(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return "onTeleportTo", proto, {proto.x, proto.y, proto.z}
end


return {
	[2] = onBroadcastPosition,
	[3] = onTeleportTo,
}
