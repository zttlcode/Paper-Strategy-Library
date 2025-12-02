from configparser import ConfigParser
import platform


def read_config(section, item):
    cp = ConfigParser()
    sys_platform = platform.platform().lower()
    if 'windows' in sys_platform:
        path = "D:\\github\\Paper-Strategy-Library\\config.ini"
    else:
        path = "/home/Paper-Strategy-Library/config_prd.ini"
    cp.read(path, encoding='utf-8')
    return cp.get(section, item)


def write_config(section, item, value):
    cp = ConfigParser()
    sys_platform = platform.platform().lower()
    if 'windows' in sys_platform:
        path = "D:\\github\\Paper-Strategy-Library\\config.ini"
    else:
        path = "/home/Paper-Strategy-Library/config_prd.ini"
    cp.read(path, encoding='utf-8')
    cp.set(section, item, value)
    with open(path, "w") as configfile:
        cp.write(configfile)
