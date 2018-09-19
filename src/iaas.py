# coding=utf-8

import click

from describe_instances import describe_instances

iaas = click.Group("iaas")
iaas.add_command(describe_instances)


if __name__ == '__main__':
    iaas()
