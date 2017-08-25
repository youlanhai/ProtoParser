
# 简易protobuf解析工具

支持在message前面加上以`//@`开头的属性，用于描述消息的额外信息，比如是上行协议还是下行协议，协议的编号，协议处理函数等。

属性的格式如下：
```
[mode, cmd, method, tag=value, ...]
```

名称  | 描述
------|------
mode  | 协议的上下行模式。上行`up`，下行是`dn`(down的缩写)
cmd   | 协议编号
method | 消息处理函数的名称
tag=value | 额外的描述信息

例如：
```protobuf
//@[up, 1001, login]
message LoginProtobuf
{
    required string userName = 1;
    required string password = 2;
}
```

转换成RPC函数大致为：
```lua
-- 客户端登录上行协议
local function login(network, userName, password)
    local proto = MsgTest.LoginProtobuf()
    proto.userName = userName
    proto.password = password
    network:sendProto(1001, proto)
end

-- 服务器收到消息。搜索自己的onLogin函数，然后去调用
local function onLogin(data)
    local proto = common.LoginProtobuf()
    proto:Parse(data)

    return "onLogin", proto, {proto.userName, proto.password}
end
```

# 用法
```sh
python do.py test/messages -output test/output
```

# 代码模板
位于`templates`目录下。目前仅写了lua语言的生成模板，可以自己扩展，注册到templates模块中。
