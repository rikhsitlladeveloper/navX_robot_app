from pydantic import BaseModel
from typing import Union, Optional


class ValidateMapping(BaseModel):
    slam_method: str


class ValidateNavigation(BaseModel):
    map_name: str
    with_virtual_walls: Optional[bool] = False
    local_planner_type: Optional[str] = "teb"


class ValidateUserRegister(BaseModel):
    username: str
    password: str
    role: str = 'user'


class ValidateUserDelete(BaseModel):
    username: str


class RespWrapper(BaseModel):
    error: Union[bool, None] = False
    message: Union[str, None] = None
    data: Union[str, dict, None] = None
