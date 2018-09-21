# qingcloud-cli

# 引用的开源库

- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) 解析 YAML 格式配置文件
- [Click](http://click.pocoo.org/5/) 用于快速创建 CLI 的 Python 库
- [Requests](http://docs.python-requests.org/en/master/) 网络请求库。

# 说明

- 针对有多值输入的参数，采用 `-p value1 -p value2 -p value3` 的形式，不必作为列表解析，例如 describe_instances 的 instances 参数。
- 针对有固定取值列表的参数，对用户输入进行检查，只能从取值列表中取，例如 describe_instances 的 instance_type 参数；
- 针对拥有取值范围的参数，对用户输入进行检查，超出范围时，回落到取值范围边界值，例如 describe_instances 的 limit 参数；
- 针对拥有默认值的参数，当用户没有指定时，使用其默认值，例如 describe_instances 的 offset 参数；
- 针对只有二元取值的参数，使用 flag 的方式，当用户指定该参数时为 1 或 True，否则为 0 或 False，例如 terminate_instances 的 direct_cease 参数；
- 针对敏感的用户输入，采用隐藏输入值的方式，例如创建配置文件时，用户输入的私钥 qy_secret_access_key 内容是隐藏的。
- 针对高危的用户操作，进行二次确认（默认为终止操作），例如 terminate_instances 时指定 direct_cease 参数直接销毁主机；
- 针对互相约束的参数，在本地进行了检查，例如 run_instances 中，instance_type 和 cpu、memeory 参数的约束关系。

# 项目结构

```
├── qingcloud					# 代码目录
│   ├── __init__.py
│   ├── base.py					# 封装 GET 请求、计算签名、常见错误处理
│   ├── common.py				# 存放参数的固定取值列表，公共回调函数等
│   ├── entry.py				# iaas 命令入口
│   ├── describe_instances.py
│   ├── gen_config_file.py		
│   ├── run_instances.py
│   └── terminate_instances.py
├── tests						# 测试用例
│   ├── __init__.py
│   └── test_base.py
├── run.py						# 直接运行入口，命令 python3 run.py --help
└── setup.py					# 打包配置文件
```

逻辑关系

```
base.py
common.py 
  ||
  ||
  \/
describe_instances.py
gen_config_file.py		
run_instances.py
terminate_instances.py
  ||
  ||
  \/
entry.py
```

# 安装

## pip 安装

由于代码中使用了 Python 3.6 引入的 “Formatted string”（参见 PEP498），因此需要 Python 版本 不低于 3.6。（实际应用时考虑到兼容性，会避免使用该语法）。

从 GitHub 安装：

```
pip install git+https://github.com/chiqj/qingcloud-cli.git
```

# 使用

所有命令都在 `iaas` 命令下调用。

```
$ iaas
Usage: iaas [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config               生成配置文件
  describe_instances   获取一台或多台主机
  run_instances        创建指定配置，指定数量的主机。
  terminate_instances  销毁一台或多台主机
```

## 创建配置文件

使用 `iaas config` 创建配置文件，可以使用 `--path` 参数指定配置文件路径。

```
$ iaas config --help
Usage: iaas config [OPTIONS]

  生成保存 API 密钥和私钥的配置文件

Options:
  --path PATH  配置文件保存路径  [default: ~/.qingcloud/config.yaml]
  -h, --help   Show this message and exit.
```

## 获取主机

使用 `iaas describe_instances` 获取主机。必传参数：可用区 `ZONE`。

```
$ iaas describe_instances -h
Usage: iaas describe_instances [OPTIONS] ZONE

  可根据主机 ID, 状态, 主机名称, 映像 ID 作过滤条件，来获取主机列表。 如果不指定任何过滤条件, 默认返回你所拥有的所有主机。

  ZONE: 区域 ID，注意要小写

Options:
  --instances TEXT                主机ID
  --image_id TEXT                 一个或多个映像ID
  --instance_type [c1m1|c1m2|c1m4|c2m2|c2m4|c2m8|c4m4|c4m8|c4m16|small_b|small_c|medium_a|medium_b|medium_c|large_a|large_b|large_c]
                                  主机配置类型
  --instance_class [0|1]          主机性能类型: 性能型:0, 超高性能型:1
  --status [pending|running|stopped|suspended|terminated|ceased]
                                  主机状态
  --search_word TEXT              搜索关键词, 支持主机ID, 主机名称
  --tags TEXT                     按照标签ID过滤, 只返回已绑定某标签的资源
  --dedicated_host_group_id TEXT  按照专属宿主机组过滤
  --dedicated_host_id TEXT        按照专属宿主机组中某个宿主机过滤
  --owner TEXT                    按照用户账户过滤, 只返回指定账户的资源
  -v, --verbose                   是否返回冗长的信息
  --offset INTEGER                数据偏移量  [default: 0]
  --limit INTEGER RANGE           返回数据长度，最大100  [default: 20]
  --config PATH                   指定配置文件  [default: ~/.qingcloud/config.yaml]
  -h, --help                      Show this message and exit.
```

## 创建主机

使用 `iaas run_instances` 创建主机。必传三个参数：可用区 `ZONE`、映象 ID `IMAGE_ID`、登录方式 `LOGIN_MODE`。

```
$ iaas run_instances -h
Usage: iaas run_instances [OPTIONS] ZONE IMAGE_ID LOGIN_MODE

  当你创建主机时，主机会先进入 pending 状态，直到创建完成后，变为 running 状态。 你可以使用 describe_instances
  检查主机状态。

  ZONE：区域 ID，注意要小写

  IMAGE_ID：映像ID，此映像将作为主机的模板。可传青云提供的映像 ID，或自己创建的映像 ID

  LOGIN_MODE：指定登录方式。当为 linux 主机时，有效值为 keypair 和 passwd; 当为 windows 主机时，只能选用
  passwd 登录方式。

Options:
  --instance_type [c1m1|c1m2|c1m4|c2m2|c2m4|c2m8|c4m4|c4m8|c4m16|small_b|small_c|medium_a|medium_b|medium_c|large_a|large_b|large_c]
                                  主机类型。如果指定了 instance_type，则 cpu 和 memory
                                  可省略；如果请求中没有 instance_type，则 cpu 和 memory
                                  参数必须指定；如果请求参数中既有 instance_type，又有 cpu 和
                                  memory，则以 cpu 和 memory 的值为准。
  --cpu [1|2|4|8|16]              CPU 核心数
  --memory [1024|2048|4096|6144|8192|12288|16384|24576|32768]
                                  内存，单位 MB
  --os_disk_size INTEGER RANGE    系统盘大小，单位 GB。Linux操作系统的有效值为：20-100，默认值为
                                  20；Windows操作系统的有效值为：50-100，默认值为 50；
  --count INTEGER                 创建主机的数量  [default: 1]
  --instance_name TEXT            主机名称
  --login_keypair TEXT            登录密钥 ID。当 login_mode 为 keypair 时，需要指定
                                  login_keypair 参数
  --login_passwd TEXT             登录密码。当 login_mode 为 passwd 时，需要指定
                                  login_passwd 参数
  --vxnets TEXT                   主机要加入的私有网络ID，如果不传此参数，则表示不加入到任何网络。如果是自建的受管私有网
                                  络（不包括基础网络 vxnet-0），则可以在创建主机时指定内网 IP，这时参数值要改为
                                  vxnet-id|ip-address ，如 vxnet-
                                  abcd123|192.168.1.2。
  --security_group TEXT           主机加载的防火墙ID，只有在 vxnets
                                  包含基础网络（即：vxnet-0）时才需要提供。若未提供，则默认加载缺省防火墙
  --volumes TEXT                  主机创建后自动加载的硬盘ID，如果传此参数，则参数 count 必须为 1。
  --hostname TEXT                 指定主机的 hostname
  --need_newsid                   是否生成新的SID，只对Windows类型主机有效。
  --instance_class [0|1]          主机性能类型: 性能型:0, 超高性能型:1
  --cpu_model [Westmere|SandyBridge|IvyBridge|Haswell|Broadwell]
                                  CPU 指令集
  --cpu_topology TEXT             CPU 拓扑结构，格式：插槽数, 核心数, 线程数；插槽数 * 核心数 * 线程数
                                  应等于您应选择的CPU数量。
  --gpu INTEGER                   GPU 个数
  --nic_mqueue                    是否开启网卡多对列
  --need_userdata                 是否使用 User Data 功能
  --userdata_type [plain|exec|tar]
                                  User Data 类型，有效值：plain, exec 或 tar。为 plain 或
                                  exec 时，使用一个 Base64 编码后的字符串；为 tar
                                  时，使用一个压缩包（种类为 zip，tar，tgz，tbz）。
  --userdata_value TEXT           User Data 值。当类型为 plain 时，为字符串的 Base64
                                  编码值，长度限制 4K；当类型为 tar 为调用
                                  UploadUserDataAttachment 返回的 attachment_id。
  --userdata_path TEXT            User Data 和 MetaData
                                  生成文件的存放路径。不输入或输入不合法时，使用默认值。  [default:
                                  /etc/qingcloud/userdata]
  --userdata_file TEXT            userdata_type 为 exec 时，指定生成可执行文件的路径
                                  [default: /etc/rc.local]
  --target_user TEXT              目标用户 ID ，可用于主账号为其子账号创建资源。
  --dedicated_host_group_id TEXT  指定专属宿主机组
  --dedicated_host_id TEXT        指定专属宿主机组中指定的宿主机
  --instance_group TEXT           指定主机组
  --config PATH                   指定配置文件  [default: ~/.qingcloud/config.yaml]
  -h, --help                      Show this message and exit.
```

## 销毁主机

使用 `iaas terminate_instances` 创建主机。必传两种参数：可用区 `ZONE`、实例 ID `INSTANCES`（可以有多个值）。

```
$ iaas terminate_instances -h
Usage: iaas terminate_instances [OPTIONS] ZONE INSTANCES...

  销毁主机的前提，是此主机已建立租用信息。 正在创建的主机以及刚刚创建成功但还没有建立租用信息的主机，是不能被销毁的。

  ZONE：区域 ID，注意要小写

  INSTANCES：一个或多个主机ID

Options:
  --direct_cease  是否直接彻底销毁主机，如果指定则会直接销毁，不会进入回收站
  --config PATH   指定配置文件  [default: ~/.qingcloud/config.yaml]
  -h, --help      Show this message and exit.
```

