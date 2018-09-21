# coding=utf-8

import os

import yaml
import click

from qingcloud.common import CONTEXT_SETTINGS, CONFIG_FILE_PATH


@click.command(short_help="生成配置文件", context_settings=CONTEXT_SETTINGS)
@click.option(
    "--path",
    type=click.Path(writable=True),
    default=CONFIG_FILE_PATH,
    show_default=True,
    help="配置文件保存路径",
)
def config(path):
    """生成保存 API 密钥和私钥的配置文件"""
    path = os.path.expanduser(path)

    # 读数据
    data = {
        "qy_access_key_id": click.prompt("qy_access_key_id"),
        "qy_secret_access_key": click.prompt(
            "qy_secret_access_key",
            hide_input=True
        ),
    }

    try:
        # 建目录
        dir_ = os.path.split(path)[0]
        if dir_ and not os.path.exists(dir_):
            os.makedirs(dir_)
        # 保存
        with open(path, "w") as f:
            f.write(yaml.dump(data))
    except Exception as e:
        click.echo(str(e), err=True)
        return

    click.echo("操作成功")
