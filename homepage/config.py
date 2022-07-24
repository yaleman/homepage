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
    """link list"""

    title: str
    favicon: Optional[str] = None
    links: List[Link]

    @validator("favicon")
    def validate_favicon(cls, value: Optional[str]) -> str:
        """ validates the favicon setting """
        if value is None:
            return "/static/favicon.svg"
        return f"/images/{value}"
