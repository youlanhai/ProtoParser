--
-- this file is auto generate by ProtoParser tool.
-- from test
local test = loadprotobuf "test"
local EMPTY_TABLE = {}


-- [7]
local function onTransformChanged(data)
	local proto = test.TransformChanged()
	proto:Parse(data)

	return proto, {proto.position, proto.rotation}
end



return {
	[7] = onTransformChanged,
}
