
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

转换成RPC函数为：
```python
# 客户端登录上行协议
def login(userName, password):
    proto = LoginProtobuf()
    proto.userName = userName
    proto.password = password
    network.send(1001, proto:SerializeToBytes())

# 服务器收到消息
def onCallLogin(userName, password):
    pass # do somthing
```

