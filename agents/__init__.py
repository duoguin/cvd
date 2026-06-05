import sys
from typing import Dict
from enum import Enum

# 1. Import base classes
from .base import BaseRole, BaseAPIHandler, BaseBot, BaseUser

# 2. Import implementations to register subclasses
from .bot import DummyBot, ReactBot, StateReactBot
from .user import DummyUser, InputUser, LLMSimulatedUserWithProfile, LLMSimulatedUserWithOOW
from .api import DummyAPIHandler, LLMSimulatedAPIHandler, RealAPIHandler

# 3. Import user profile and output objects
from .user_profile import UserProfile, OOWIntention
from .role_outputs import BotOutput, UserOutput, APIOutput, BotOutputType

# 4. Helper to build registration mapping dynamically
def build_attr_list_map(base_class, name_to_class_dict: Dict, attr: str="names"):
    for cls in base_class.__subclasses__():
        if attr in cls.__dict__ and cls.__dict__[attr]:
            names = cls.__dict__[attr]
            if isinstance(names, str):
                names = [names]
            for name in names:
                name_to_class_dict[name] = cls
        # recursive!
        build_attr_list_map(cls, name_to_class_dict, attr)

USER_NAME2CLASS = {}
build_attr_list_map(BaseUser, USER_NAME2CLASS)

BOT_NAME2CLASS = {}
build_attr_list_map(BaseBot, BOT_NAME2CLASS)

API_NAME2CLASS = {}
build_attr_list_map(BaseAPIHandler, API_NAME2CLASS)

# 5. Typer helper and dynamic enums
def create_enum(name, values):
    return Enum(name, {key: key for key in values})

UserMode = create_enum('UserMode', USER_NAME2CLASS.keys())
BotMode = create_enum('BotMode', BOT_NAME2CLASS.keys())
ApiMode = create_enum('ApiMode', API_NAME2CLASS.keys())
