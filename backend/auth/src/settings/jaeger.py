import pydantic
from pydantic import (
    BaseModel,
    Field,
)


class JaegerSettings(BaseModel):
    agent_host: str = Field(alias="jaeger_agent_host", default="localhost")
    agent_port: int = Field(alias="jaeger_agent_port", default=6831)
    service_name: str = Field(alias="jaeger_service_name")
    enabled: bool = Field(alias="jaeger_enabled", default=False)
