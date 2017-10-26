--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"
local EMPTY_TABLE = {}


-- [1]
local function onSendPosition(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return proto, {proto.x, proto.y, proto.z}
end


-- [1000]
local function onSetRotation(data)
	local proto = common.Vector4()
	proto:Parse(data)

	return proto, EMPTY_TABLE
end


-- [1001]
local function onLogin(data)
	local proto = common.LoginProtobuf()
	proto:Parse(data)

	return proto, {proto.userName, proto.password}
end



return {
	[1] = onSendPosition,
	[1000] = onSetRotation,
	[1001] = onLogin,
}
