# coding=utf-8

from pprint import pformat

import click

from src.base import QingCloudBase
from src.common import validate_config_file, CONFIG_FILE_PATH, \
    INSTANCE_TYPE_LIST, INSTANCE_CLASS_LIST, STATUS_LIST


@click.command(short_help="获取一台或多台主机")
@click.option("--instances", "-i", multiple=True, help="主机ID")
@click.option("--image_id", "-m", multiple=True, help="一个或多个映像ID")
@click.option(
    "--instance_type",
    "-t",
    multiple=True,
    type=click.Choice(INSTANCE_TYPE_LIST),
    help="主机配置类型",
)
@click.option(
    "--instance_class",
    type=click.Choice(INSTANCE_CLASS_LIST),
    help="主机性能类型: 性能型:0, 超高性能型:1",
)
@click.option(
    "--status",
    multiple=True,
    type=click.Choice(STATUS_LIST),
    help="主机状态"
)
@click.option("--search_word", help="搜索关键词, 支持主机ID, 主机名称")
@click.option("--tags", multiple=True, help="按照标签ID过滤, 只返回已绑定某标签的资源")
@click.option("--dedicated_host_group_id", help="按照专属宿主机组过滤")
@click.option("--dedicated_host_id", help="按照专属宿主机组中某个宿主机过滤")
@click.option("--owner", help="按照用户账户过滤, 只返回指定账户的资源")
@click.option("--verbose", count=True, help="是否返回冗长的信息")
@click.option(
    "--offset",
    type=int,
    default=0,
    show_default=True,
    help="数据偏移量"
)
@click.option(
    "--limit",
    type=click.IntRange(1, 100, clamp=True),
    default=20,
    show_default=True,
    help="返回数据长度，最大100",
)
@click.option(
    "--config",
    type=click.Path(),
    callback=validate_config_file,
    default=CONFIG_FILE_PATH,
    show_default=True,
    help="指定配置文件",
)
@click.argument("zone", required=True)
def describe_instances(**kw):
    """
    可根据主机 ID, 状态, 主机名称, 映像 ID 作过滤条件，来获取主机列表。
    如果不指定任何过滤条件, 默认返回你所拥有的所有主机。

    ZONE: 区域 ID，注意要小写
    """
    params = dict(action="DescribeInstances")

    # 可以传多个参数的 option
    for name in ("instances", "image_id", "instance_type", "status", "tags"):
        for idx, value in enumerate(kw[name]):
            params[f"{name}.{idx+1}"] = value       # noqa: ignore=E999

    # 只传一个参数的 option
    for name in (
                "instance_class", "search_word", "dedicated_host_group_id",
                "dedicated_host_id", "owner"
            ):
        if kw[name] is not None:
            params[name] = kw[name]

    # 计数参数，目前只支持一个，所以强制置为 1
    if kw["verbose"] > 0:
        params["verbose"] = 1

    # 拥有默认值的参数
    params["offset"] = kw["verbose"] if kw["verbose"] >= 0 else 0
    params["limit"] = kw["limit"]

    params["zone"] = kw["zone"].lower()

    # 构造请求类，发起请求
    qc_base = QingCloudBase(**kw["config"])
    response = qc_base.get(params)

    # 美化格式后输出
    click.echo(pformat(response))


if __name__ == '__main__':
    describe_instances()
