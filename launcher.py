import signal
import subprocess
from enum import Enum, auto
from typing import Any, List, Union, Optional
from utils import username, config


class LaunchState(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: List[Any]) -> Any:
        return self

    BRINGUP = auto()
    MAPPING = auto()
    NAVIGATION = auto()
    OFF = auto()

class ProcessState(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: List[Any]) -> Any:
        return self

    RUNNING = auto()
    STOPPED = auto()
    ERROR = auto()
    NONE = auto()

class Launcher:
    __process_bringup: Union[subprocess.Popen, None] = None
    __process_mapping: Union[subprocess.Popen, None] = None
    __process_navigation: Union[subprocess.Popen, None] = None
    state = LaunchState.OFF

    @classmethod
    def start_bringup(cls):
        with open(f"/home/{username}/.logs/bringup_output.log", "w") as out, \
                open(f"/home/{username}/.logs/bringup_error.log", "w") as err:
            cls.__process_bringup = subprocess.Popen(["ros2", "launch", config["amr_ros_pkg_name"], config["bringup_launch"]],
                                                     stdout=out, stderr=err)
        cls.state = LaunchState.BRINGUP

    @classmethod
    def start_mapping(cls, slam_method):
        with open(f"/home/{username}/.logs/mapping_output.log", "w") as out, \
                open(f"/home/{username}/.logs/mapping_error.log", "w") as err:
            cls.__process_mapping = subprocess.Popen(["ros2", "launch", config["amr_ros_pkg_name"], config["slam_launch"]],
                                                     stdout=out, stderr=err)
        cls.state = LaunchState.MAPPING

    @classmethod
    def start_navigation(cls, map_name, local_planner_type, with_virtual_walls=False):
        with open(f"/home/{username}/.logs/navigation_output.log", "w") as out, \
                open(f"/home/{username}/.logs/navigation_error.log", "w") as err:
            cls.__process_navigation = subprocess.Popen(["ros2", "launch", config["amr_ros_pkg_name"], config["navigation_launch"],
                                                         "map:=/home/nvidia/maps/" + map_name + ".yaml" ,
                                                        #  "local_planner_type:=" + local_planner_type,
                                                        #  "with_virtual_walls:=" + str(with_virtual_walls).lower()
                                                        ],
                                                        stdout=out, stderr=err)
        cls.state = LaunchState.NAVIGATION

    @classmethod
    def stop_bringup(cls):
        if cls.__process_bringup is not None:
            cls.__process_bringup.send_signal(signal.SIGINT)
            cls.__process_bringup.wait()
            cls.state = LaunchState.OFF

    @classmethod
    def stop_mapping(cls):
        if cls.__process_mapping is not None:
            cls.__process_mapping.send_signal(signal.SIGINT)
            cls.__process_mapping.wait()
            cls.state = LaunchState.BRINGUP

    @classmethod
    def stop_navigation(cls):
        if cls.__process_navigation is not None:
            cls.__process_navigation.send_signal(signal.SIGINT)
            cls.__process_navigation.wait()
            cls.state = LaunchState.BRINGUP

    @classmethod
    def bringup_state(cls) -> ProcessState:
        if cls.__process_bringup is not None:
            if cls.__process_bringup.poll() is None:
                return ProcessState.RUNNING
            else:
                if cls.__process_bringup.returncode == 0:
                    cls.stop_bringup()
                    return ProcessState.STOPPED
                else:
                    cls.stop_bringup()
                    return ProcessState.ERROR
        else:
            return ProcessState.NONE

    @classmethod
    def mapping_state(cls) -> ProcessState:
        if cls.__process_mapping is not None:
            if cls.__process_mapping.poll() is None:
                return ProcessState.RUNNING
            else:
                if cls.__process_mapping.returncode == 0:
                    cls.stop_mapping()
                    return ProcessState.STOPPED
                else:
                    cls.stop_mapping()
                    return ProcessState.ERROR
        else:
            return ProcessState.NONE

    @classmethod
    def navigation_state(cls) -> ProcessState:
        if cls.__process_navigation is not None:
            if cls.__process_navigation.poll() is None:
                return ProcessState.RUNNING
            else:
                if cls.__process_navigation.returncode == 0:
                    cls.stop_navigation()
                    return ProcessState.STOPPED
                else:
                    cls.stop_navigation()
                    return ProcessState.ERROR
        else:
            return ProcessState.NONE

    @classmethod
    def bringup_pid(cls) -> Optional[int]:
        if cls.__process_bringup is not None:
            return cls.__process_bringup.pid
        else: return None

    @classmethod
    def mapping_pid(cls) -> Optional[int]:
        if cls.__process_mapping is not None:
            return cls.__process_mapping.pid
        else: return None

    @classmethod
    def navigation_pid(cls) -> Optional[int]:
        if cls.__process_navigation is not None:
            return cls.__process_navigation.pid
        else: return None