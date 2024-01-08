from pydantic import (
    BaseModel,
    Field,
)


class ServiceSettings(BaseModel):
    name: str = Field(alias="service_name")
    host: str = Field(alias="service_host")
    port: int = Field(alias="service_port")
    debug: bool = Field(
        alias="service_debug",
        default=False,
    )

    description: str = Field(
        alias="service_description",
        default="",
    )
