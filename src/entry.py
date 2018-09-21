# coding=utf-8

import click

from src.describe_instances import describe_instances
from src.terminate_instances import terminate_instances
from src.run_instances import run_instances

iaas = click.Group("iaas")

iaas.add_command(describe_instances)
iaas.add_command(terminate_instances)
iaas.add_command(run_instances)
