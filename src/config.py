# coding=utf-8

CONFIG_FILE_PATH = "~/.qingcloud/config.yaml"

INSTANCE_TYPE_LIST = [
    "c1m1", "c1m2", "c1m4", "c2m2", "c2m4", "c2m8", "c4m4", "c4m8", "c4m16",
    "small_b", "small_c", "medium_a", "medium_b", "medium_c", "large_a",
    "large_b", "large_c",
]

INSTANCE_CLASS_LIST = ["0", "1"]

STATUS_LIST = [
    "pending", "running", "stopped", "suspended", "terminated", "ceased"
]

CPU_LIST = ["1", "2", "4", "8", "16"]

MEMORY_LIST = [
    "1024", "2048", "4096", "6144", "8192", "12288", "16384", "24576", "32768"
]

CPU_MODEL_LIST = [
    "Westmere", "SandyBridge", "IvyBridge", "Haswell", "Broadwell"
]

USERDATA_TYPE_LIST = ["plain", "exec", "tar"]
