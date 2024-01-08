from pydantic import BaseModel, Field


class JaegerSettings(BaseModel):
    agent_host: str = Field(alias="jaeger_agent_host")
    agent_port: int = Field(alias="jaeger_agent_port")
    service_name: str = Field(alias="jaeger_service_name")
    enabled: bool = Field(alias="jaeger_enabled", default=False)
