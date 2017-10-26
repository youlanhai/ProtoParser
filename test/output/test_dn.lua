--
-- this file is auto generate by ProtoParser tool.
-- from test
local test = loadprotobuf "test"


-- [7]
local function onTransformChanged(network, position, rotation)
	local proto = test.TransformChanged()
	proto.position = position
	proto.rotation = rotation
	network:sendProto(7, proto)
end



return {
	onTransformChanged = onTransformChanged,
}
