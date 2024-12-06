import glob
import rospkg
import re
from typing import List, Union, Tuple
import yaml
import os
from os import path
import zipfile
import getpass
from ament_index_python.packages import get_package_share_directory



def get_config() -> dict:
    default_config = {
        "amr_ros_pkg_name": "navigationx_robot",
        "bringup_launch": "bringup_launch.py",
        "slam_launch": "slam_toolbox.launch.py",
        "navigation_launch": "navigation2.launch.py"
        }
    with open("appconfig.yaml", "r") as conf_file:
        appconfig = yaml.load(conf_file, Loader=yaml.FullLoader)
    if all(item in appconfig.keys() for item in default_config.keys()):
        return appconfig
    return default_config


username = getpass.getuser()
rospack = rospkg.RosPack()
config = get_config()
amr_robot_path = get_package_share_directory(config["amr_ros_pkg_name"])
# amr_robot_path = rospack.get_path(config["amr_ros_pkg_name"])
amr_robot_maps =  '/home/nvidia/maps/'
slam_methods = os.listdir(os.path.join(amr_robot_path, 'launch'))
slam_methods = [method.partition('.')[0] for method in slam_methods]


def check_filename_ex(filename: str, directory: str) -> bool:
    filename_pattern = r'(.+?)(\.[^.]*$|$)'
    names = set()
    files = [file for file in os.listdir(directory) if os.path.isfile(directory + file)]
    for file in files:
        match = re.search(filename_pattern, file)
        names.add(match.group(1))
    if filename in names:
        return True
    return False


def check_file_ex(filename: str, extension: str, directory: str) -> bool:
    if os.path.isfile(directory + filename + '.' + extension):
        return True
    return False


def get_ext_maps() -> List[Tuple[str, Union[str, bytes], Union[str, bytes], str]]:
    ext_maps = []
    all_maps_yaml = glob.glob(amr_robot_maps + '*.yaml')
    for map_yaml in all_maps_yaml:
        with open(map_yaml) as file:
            map_descr = yaml.load(file, Loader=yaml.FullLoader)
            if map_descr is not None and 'image' in map_descr.keys():
                map_pgm = path.join(amr_robot_maps, path.basename(map_descr['image']))
                map_name = path.basename(map_yaml).partition('.')[0]
                map_png = str(map_pgm.partition('.')[0]) + '.png'
                if path.isfile(map_pgm):
                    if not path.isfile(map_png):
                        os.system("convert" + " " + map_pgm + " " + map_png)
                    ext_maps.append((map_name, map_yaml, map_pgm, map_png))
                file.close()
    return ext_maps


def compress_maps() -> None:
    for map_name, map_yaml, map_pgm, map_png in get_ext_maps():
        map_zip = os.path.join(amr_robot_maps, f'{map_name}.zip')
        if os.path.isfile(map_zip):
            pass
        else:
            with zipfile.ZipFile(map_zip, mode='w') as archive:
                archive.write(filename=map_yaml, arcname=os.path.basename(map_yaml))
                archive.write(filename=map_pgm, arcname=os.path.basename(map_pgm))
                archive.write(filename=map_png, arcname=os.path.basename(map_png))
                archive.close()


def extract_map(filename: str) -> None:
    with zipfile.ZipFile(filename) as file:
        file.extractall(amr_robot_maps)
