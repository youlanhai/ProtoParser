--
-- this file is auto generate by ProtoParser tool.
-- from common
local common = loadprotobuf "common"


-- [1]
local function sendPosition(network, x, y, z)
	local proto = common.Vector3()
	proto.x = x
	proto.y = y
	proto.z = z
	network:sendProto(1, proto)
end


-- [1000]
local function setRotation(network, proto)
	network:sendProto(1000, proto)
end


-- [1001]
local function login(network, userName, password)
	local proto = common.LoginProtobuf()
	proto.userName = userName
	proto.password = password
	network:sendProto(1001, proto)
end



return {
	login = login,
	sendPosition = sendPosition,
	setRotation = setRotation,
}
