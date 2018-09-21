# coding=utf-8

import click

from describe_instances import describe_instances
from terminate_instances import terminate_instances
from run_instances import run_instances

iaas = click.Group("iaas")

iaas.add_command(describe_instances)
iaas.add_command(terminate_instances)
iaas.add_command(run_instances)
