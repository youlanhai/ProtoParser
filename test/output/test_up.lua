--
-- this file is auto generate by ProtoParser tool.
-- from test
local test = loadprotobuf "test"


-- [6]
local function sendTransform(network, position, rotation)
	local proto = test.TransformChanged()
	proto.position = position
	proto.rotation = rotation
	network:sendProto(6, proto)
end



return {
	sendTransform = sendTransform,
}
