--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"
local EMPTY_TABLE = {}


-- [2]
local function onBroadcastPosition(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return proto, {proto.x, proto.y, proto.z}
end


-- [3]
local function onTeleportTo(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return proto, {proto.x, proto.y, proto.z}
end



return {
	[2] = onBroadcastPosition,
	[3] = onTeleportTo,
}
