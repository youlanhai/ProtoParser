--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"


local function onSendPosition(data)
	local proto = common.Vector3()
	proto:Parse(data)

	return "onSendPosition", proto, {proto.x, proto.y, proto.z}
end


local function onSetRotation(data)
	local proto = common.Vector4()
	proto:Parse(data)

	return "onSetRotation", proto, {}
end


local function onLogin(data)
	local proto = common.LoginProtobuf()
	proto:Parse(data)

	return "onLogin", proto, {proto.userName, proto.password}
end


return {
	[1] = sendPosition,
	[1000] = setRotation,
	[1001] = login,
}
