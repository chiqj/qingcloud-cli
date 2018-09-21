# coding=utf-8

import os

import yaml
import click


def validate_config_file(ctx, param, value):
    path = os.path.expanduser(value)
    # 检查文件存在
    if not os.path.isfile(path):
        raise click.BadParameter(f"Config file \"{path}\" not exists.")     # noqa: ignore=E999
    # 读取
    try:
        with open(path, "r") as f:
            result = yaml.load(f)
        return {
            "qy_access_key_id": result["qy_access_key_id"],
            "qy_secret_access_key": result["qy_secret_access_key"],
        }
    except:         # noqa: ignore=E722
        raise click.BadParameter(f"Config file \"{path}\" format error.")
