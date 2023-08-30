""" config object """

from pathlib import Path
from typing import List, Optional

from pydantic import field_validator, BaseModel
from pydantic_settings import BaseSettings

DEFAULT_ICON = "default.png"
DEFAULT_COLOUR = "white"

class Link(BaseModel):
    """link object"""

    url: str
    title: str
    icon: Optional[str] = DEFAULT_ICON
    colour: Optional[str] = DEFAULT_COLOUR


class ConfigFile(BaseSettings):
    """ config file things """
    favicon: Optional[str] = None
    links: List[Link]
    open_in_new_tab: Optional[bool] = False
    title: str

    @field_validator("favicon")
    @classmethod
    def validate_favicon(cls, value: Optional[str]) -> str:
        """ validates the favicon setting """
        if value is None:
            return "/static/favicon.svg"
        return f"/images/{value}"

def load_config(filename: Path) -> Optional[ConfigFile]:
    """ load a config file from a filepath """
    if not filename.exists():
        return None
    return ConfigFile.model_validate_json(filename.read_text(encoding="utf-8"))