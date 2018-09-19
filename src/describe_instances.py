# coding=utf-8

import os
from pprint import pformat

import click

from base import QingCloudBase

INSTANCE_TYPE_CHOICE = click.Choice([
    "c1m1", "c1m2", "c1m4", "c2m2", "c2m4", "c2m8", "c4m4", "c4m8", "c4m16",
    "small_b", "small_c", "medium_a", "medium_b", "medium_c", "large_a",
    "large_b", "large_c",
])
INSTANCE_CLASS_CHOICE = click.Choice(["0", "1"])
STATUS_CHOICE = click.Choice([
    "pending", "running", "stopped", "suspended", "terminated", "ceased"
])


@click.command(short_help="获取一个或多个主机")
@click.option("--instances", "-i", multiple=True, help="主机ID")
@click.option("--image_id", "-m", multiple=True, help="一个或多个映像ID")
@click.option(
    "--instance_type",
    "-t",
    multiple=True,
    type=INSTANCE_TYPE_CHOICE,
    help="主机配置类型",
)
@click.option(
    "--instance_class",
    type=INSTANCE_CLASS_CHOICE,
    help="主机性能类型: 性能型:0, 超高性能型:1",
)
@click.option("--status", multiple=True, type=STATUS_CHOICE, help="主机状态")
@click.option("--search_word", help="搜索关键词, 支持主机ID, 主机名称")
@click.option("--tags", multiple=True, help="按照标签ID过滤, 只返回已绑定某标签的资源")
@click.option("--dedicated_host_group_id", help="按照专属宿主机组过滤")
@click.option("--dedicated_host_id", help="按照专属宿主机组中某个宿主机过滤")
@click.option("--owner", help="按照用户账户过滤, 只返回指定账户的资源")
@click.option("--verbose", count=True, help="是否返回冗长的信息")
@click.option("--offset", type=int, default=0, help="数据偏移量, 默认为0")
@click.option(
    "--limit",
    type=click.IntRange(1, 100, clamp=True),
    default=20,
    help="返回数据长度，默认为20，最大100",
)
@click.option("--zone", prompt=True, help="区域 ID，注意要小写")
def describe_instances(**kw):
    """
    可根据主机 ID, 状态, 主机名称, 映像 ID 作过滤条件，来获取主机列表。
    如果不指定任何过滤条件, 默认返回你所拥有的所有主机。
    """
    params = dict(action="DescribeInstances")

    # 可以传多个参数的 option
    for name in ("instances", "image_id", "instance_type", "status", "tags"):
        for idx, value in enumerate(kw[name]):
            params[f"{name}.{idx+1}"] = value       # noqa: ignore=E999

    # 只传一个参数的 option
    for name in (
                "instance_class", "search_word", "dedicated_host_group_id",
                "dedicated_host_id", "owner", "zone"
            ):
        if kw[name] is not None:
            params[name] = kw[name]

    # 计数参数，目前只支持一个，所以强制置为 1
    if kw["verbose"] > 0:
        params["verbose"] = 1

    # 拥有默认值的参数
    params["offset"] = kw["verbose"] if kw["verbose"] >= 0 else 0
    params["limit"] = kw["limit"]

    # 获取 API 密钥 和 API 密钥的私钥
    access_key_id = os.environ.get("ACCESS_KEY_ID")
    secret_access_key = os.environ.get("SECRET_ACCESS_KEY")

    # 构造请求类，发起请求
    qc_base = QingCloudBase(access_key_id, secret_access_key)
    response = qc_base.get(params)

    # 美化格式后输出
    click.echo(pformat(response))


if __name__ == '__main__':
    describe_instances()
