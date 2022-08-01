""" config object """

from typing import List, Optional

from pydantic import BaseSettings, BaseModel, validator


class Link(BaseModel):
    """link object"""

    url: str
    title: str
    icon: Optional[str] = "default.png"
    colour: Optional[str] = "white"


class ConfigFile(BaseSettings):
    """ config file things """
    favicon: Optional[str] = None
    links: List[Link]
    open_in_new_tab: Optional[bool] = False
    title: str

    @validator("favicon")
    def validate_favicon(cls, value: Optional[str]) -> str:
        """ validates the favicon setting """
        if value is None:
            return "/static/favicon.svg"
        return f"/images/{value}"
