# coding=utf-8

from setuptools import setup, find_packages

entry_points = """
[console_scripts]
iaas=src.entry:iaas
"""

setup(
    name="qingcloud-iaas",
    version="1.0",
    description="基于 QingCloud API 实现命令行接口",
    long_description="包括：RunInstances，DescribeInstances，TerminateInstances",
    url="https://github.com/chiqj/qingcloud-cli",
    author="chiqj",
    author_email="chiqingjun@gmail.com",
    license="MIT",

    # test_suite="test",
    packages=["src"],
    include_package_data=True,
    install_requires=["click", "requests", "PyYAML"],

    entry_points=entry_points,
)
