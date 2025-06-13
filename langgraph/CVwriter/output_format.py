from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import TypedDict, Annotated, List
import ast
import json

class user_info_json(TypedDict):
    """output user infomation extract from the user cv"""
    full_name: Annotated[str , "Jone Doe", "provided full name of the user"] 
    linkedin: Annotated[str , None, "LinkedIn account link if provided"]
    github: Annotated[str , None, "Github account link if provided"]
    email: Annotated[str, None, "user email address if provided"]
    mobile_number: Annotated[str, None, "user telephone or mobile number"]

class position_worked(TypedDict):
    "output position worked"
    position: Annotated[List[str], "professional experience"]
    
