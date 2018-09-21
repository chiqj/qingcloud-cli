# coding=utf-8

from pprint import pformat

import click

from qingcloud.base import QingCloudBase
from qingcloud.common import validate_config_file, CONFIG_FILE_PATH, \
    INSTANCE_TYPE_LIST, CPU_LIST, MEMORY_LIST, INSTANCE_CLASS_LIST, \
    CPU_MODEL_LIST, USERDATA_TYPE_LIST, CONTEXT_SETTINGS


def validate_login_mode(ctx, param, value):
    """限定 login_mode 输入"""
    choice = ("keypair", "passwd")
    if value not in choice:
        raise click.BadParameter(
            f"invalid choice: {value}. (choose from {', '.join(choice)})"   # noqa:ignore=E999
        )
    return value


@click.command(
    short_help="创建指定配置，指定数量的主机。",
    context_settings=CONTEXT_SETTINGS
)
@click.option(
    "--instance_type",
    type=click.Choice(INSTANCE_TYPE_LIST),
    help=(
        "主机类型。如果指定了 instance_type，则 cpu 和 memory 可省略；"
        "如果请求中没有 instance_type，则 cpu 和 memory 参数必须指定；"
        "如果请求参数中既有 instance_type，又有 cpu 和 memory，"
        "则以 cpu 和 memory 的值为准。"
    )
)
@click.option(
    "--cpu",
    type=click.Choice(CPU_LIST),
    help="CPU 核心数",
)
@click.option(
    "--memory",
    type=click.Choice(MEMORY_LIST),
    help="内存，单位 MB",
)
@click.option(
    "--os_disk_size",
    type=click.IntRange(20, 100),
    help=(
        "系统盘大小，单位 GB。"
        "Linux操作系统的有效值为：20-100，默认值为 20；"
        "Windows操作系统的有效值为：50-100，默认值为 50；"
    )
)
@click.option(
    "--count",
    type=int,
    default=1,
    show_default=1,
    help="创建主机的数量",
)
@click.option("--instance_name", help="主机名称")
@click.option(
    "--login_keypair",
    help="登录密钥 ID。当 login_mode 为 keypair 时，需要指定 login_keypair 参数",
)
@click.option(
    "--login_passwd",
    help="登录密码。当 login_mode 为 passwd 时，需要指定 login_passwd 参数",
)
@click.option(
    "--vxnets",
    multiple=True,
    help=(
        "主机要加入的私有网络ID，如果不传此参数，则表示不加入到任何网络。"
        "如果是自建的受管私有网络（不包括基础网络 vxnet-0），则可以在创建主机时指定内网 IP，"
        "这时参数值要改为 vxnet-id|ip-address ，如 vxnet-abcd123|192.168.1.2。"
    )
)
@click.option(
    "--security_group",
    help=(
        "主机加载的防火墙ID，只有在 vxnets 包含基础网络（即：vxnet-0）时才需要提供。"
        "若未提供，则默认加载缺省防火墙"
    )
)
@click.option(
    "--volumes",
    multiple=True,
    help=(
        "主机创建后自动加载的硬盘ID，如果传此参数，则参数 count 必须为 1。"
    ),
)
@click.option("--hostname", help="指定主机的 hostname")
@click.option(
    "--need_newsid",
    is_flag=True,
    default=False,
    help="是否生成新的SID，只对Windows类型主机有效。"
)
@click.option(
    "--instance_class",
    type=click.Choice(INSTANCE_CLASS_LIST),
    help="主机性能类型: 性能型:0, 超高性能型:1",
)
@click.option(
    "--cpu_model",
    type=click.Choice(CPU_MODEL_LIST),
    help="CPU 指令集",
)
@click.option(
    "--cpu_topology",
    help=(
        "CPU 拓扑结构，格式：插槽数, 核心数, 线程数；"
        "插槽数 * 核心数 * 线程数 应等于您应选择的CPU数量。"
    ),
)
@click.option(
    "--gpu",
    type=int,
    help="GPU 个数",
)
@click.option(
    "--nic_mqueue",
    is_flag=True,
    default=False,
    help="是否开启网卡多对列",
)
@click.option(
    "--need_userdata",
    is_flag=True,
    default=False,
    help="是否使用 User Data 功能",
)
@click.option(
    "--userdata_type",
    type=click.Choice(USERDATA_TYPE_LIST),
    help=(
        "User Data 类型，有效值：plain, exec 或 tar。"
        "为 plain 或 exec 时，使用一个 Base64 编码后的字符串；"
        "为 tar 时，使用一个压缩包（种类为 zip，tar，tgz，tbz）。"
    )
)
@click.option(
    "--userdata_value",
    help=(
        "User Data 值。"
        "当类型为 plain 时，为字符串的 Base64 编码值，长度限制 4K；"
        "当类型为 tar 为调用 UploadUserDataAttachment 返回的 attachment_id。"
    ),
)
@click.option(
    "--userdata_path",
    default="/etc/qingcloud/userdata",
    show_default=True,
    help="User Data 和 MetaData 生成文件的存放路径。不输入或输入不合法时，使用默认值。",
)
@click.option(
    "--userdata_file",
    default="/etc/rc.local",
    show_default=True,
    help="userdata_type 为 exec 时，指定生成可执行文件的路径",
)
@click.option(
    "--target_user",
    help="目标用户 ID ，可用于主账号为其子账号创建资源。"
)
@click.option("--dedicated_host_group_id", help="指定专属宿主机组")
@click.option("--dedicated_host_id", help="指定专属宿主机组中指定的宿主机")
@click.option("--instance_group", help="指定主机组")
@click.option(
    "--config",
    type=click.Path(),
    callback=validate_config_file,
    default=CONFIG_FILE_PATH,
    show_default=True,
    help="指定配置文件",
)
@click.argument("zone", required=True)
@click.argument("image_id", required=True)
@click.argument("login_mode", required=True, callback=validate_login_mode)
def run_instances(**kw):
    """
    当你创建主机时，主机会先进入 pending 状态，直到创建完成后，变为 running 状态。
    你可以使用 describe_instances 检查主机状态。

    ZONE：区域 ID，注意要小写

    IMAGE_ID：映像ID，此映像将作为主机的模板。可传青云提供的映像 ID，或自己创建的映像 ID

    LOGIN_MODE：指定登录方式。当为 linux 主机时，有效值为 keypair 和 passwd;
    当为 windows 主机时，只能选用 passwd 登录方式。

    """
    params = dict(action="RunInstances")

    # 必传的 argument
    params["zone"] = kw["zone"].lower()
    params["image_id"] = kw["image_id"]
    params["login_mode"] = kw["login_mode"]

    # instance_type 和 cpu + memory 限制
    if kw["cpu"] and kw["memory"]:
        params["cpu"] = kw["cpu"]
        params["memory"] = kw["memory"]
    elif kw["instance_type"]:
        params["instance_type"] = kw["instance_type"]
    else:
        click.echo(
            "[instance_type] should be specified "
            "or specify both [cpu] and [memory]",
            err=True,
        )
        return

    # login_keypair，当登录方式为 keypair 时，需要指定 login_keypair 参数
    if kw["login_mode"] == "keypair":
        if kw["login_keypair"]:
            params["login_keypair"] = kw["login_keypair"]
        else:
            click.echo(
                "[login_keypair] should be specified in keypair login mode",
                err=True,
            )
            return

    # login_passwd，当登录方式为 passwd 时，需要指定 login_passwd 参数
    if kw["login_mode"] == "passwd":
        if kw["login_passwd"]:
            params["login_passwd"] = kw["login_passwd"]
        else:
            click.echo(
                "[login_passwd] should be specified in password login mode",
                err=True,
            )
            return

    # security_group，只有在 vxnets.n 包含基础网络（即：vxnet-0）时才需要提供。
    if "vxnet-0" in kw["vxnets"] and kw["security_group"]:
        params["security_group"] = kw["security_group"]

    # volumes，如果传此参数，则参数 count 必须为1 。
    if kw["count"] != 1 and kw["volumes"]:
        click.echo(
            "[volumes] could be specified only when [count] is 1",
            err=True
        )
        return

    # userdata_value，当 userdata_type 为 plain 或 tar 时有效
    if kw["userdata_type"] in ("plain", "tar") and kw["userdata_value"]:
        params["userdata_value"] = kw["userdata_value"]

    # userdata_file，当 userdata_type 为 exec 时有效
    if kw["userdata_type"] == "exec" and kw["userdata_file"]:
        params["userdata_file"] = kw["userdata_file"]

    # 只传一个参数的 option
    for name in (
                "os_disk_size", "count", "instance_name", "hostname",
                "instance_class", "cpu_model", "cpu_topology", "gpu",
                "userdata_type", "userdata_path", "target_user",
                "dedicated_host_group_id", "dedicated_host_id",
                "instance_group"
            ):
        if kw[name] is not None:
            params[name] = kw[name]

    # flag 参数
    for name in ("nic_mqueue", "need_newsid", "need_userdata"):
        params[name] = int(kw[name])

    # 可以传多个参数的 option
    for name in ("vxnets", "volumes"):
        for idx, value in enumerate(kw[name]):
            params[f"{name}.{idx+1}"] = value       # noqa: ignore=E999

    # 构造请求类，发起请求
    qc_base = QingCloudBase(**kw["config"])
    response = qc_base.get(params)

    # 美化格式后输出
    click.echo(pformat(response))
