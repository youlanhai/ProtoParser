
TEMPLATE = """
-- this file is auto generate by ProtoParser tool.

return {
#for fileName, pckageName in $packages
	["$fileName"] = "$pckageName",
#end for
}
"""
