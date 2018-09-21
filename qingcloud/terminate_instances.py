# coding=utf-8

from pprint import pformat

import click

from qingcloud.base import QingCloudBase
from qingcloud.common import validate_config_file, CONFIG_FILE_PATH, \
    CONTEXT_SETTINGS


@click.command(short_help="销毁一台或多台主机", context_settings=CONTEXT_SETTINGS)
@click.option(
    "--direct_cease",
    is_flag=True,
    default=False,
    help="是否直接彻底销毁主机，如果指定则会直接销毁，不会进入回收站",
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
@click.argument("instances", nargs=-1, required=True)
def terminate_instances(**kw):
    """
    销毁主机的前提，是此主机已建立租用信息。
    正在创建的主机以及刚刚创建成功但还没有建立租用信息的主机，是不能被销毁的。

    ZONE：区域 ID，注意要小写

    INSTANCES：一个或多个主机ID
    """
    params = dict(action="TerminateInstances")

    # 直接销毁二次确认，默认为 False，为 False 时取消操作
    if kw["direct_cease"]:
        click.confirm("确定要直接彻底销毁吗？", abort=True)
        params["direct_cease"] = 1

    for idx, value in enumerate(kw["instances"]):
        params[f"instances.{idx+1}"] = value       # noqa: ignore=E999

    params["zone"] = kw["zone"].lower()

    # 构造请求类，发起请求
    qc_base = QingCloudBase(**kw["config"])
    response = qc_base.get(params)

    # 美化格式后输出
    click.echo(pformat(response))
