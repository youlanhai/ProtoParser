--
-- this file is auto generate by ProtoParser tool.
-- from messages
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

--
-- this file is auto generate by ProtoParser tool.
-- from messages
local test = loadprotobuf "test"
local EMPTY_TABLE = {}


-- [7]
local function onTransformChanged(data)
	local proto = test.TransformChanged()
	proto:Parse(data)

	return proto, {proto.position, proto.rotation}
end



return {
	[2] = onBroadcastPosition,
	[3] = onTeleportTo,
	[7] = onTransformChanged,
}
