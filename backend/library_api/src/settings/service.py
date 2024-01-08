from pydantic import BaseModel, Field


class ServiceSettings(BaseModel):
    name: str = Field(alias="service_name")
    host: str = Field(alias="service_host")
    port: int = Field(alias="service_port")

    description: str = Field(alias="service_description", default="")

    default_page_size: int = 50
    debug: bool = Field(False, alias="debug")
