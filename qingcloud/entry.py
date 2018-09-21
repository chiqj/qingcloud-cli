# coding=utf-8

import click

from qingcloud.describe_instances import describe_instances
from qingcloud.terminate_instances import terminate_instances
from qingcloud.run_instances import run_instances

iaas = click.Group("iaas")

iaas.add_command(describe_instances)
iaas.add_command(terminate_instances)
iaas.add_command(run_instances)
